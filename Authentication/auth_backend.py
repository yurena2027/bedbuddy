# auth_backend.py
from __future__ import annotations
import os, sqlite3, secrets, time, json
from dataclasses import dataclass
from typing import Optional, Iterable, Tuple, List
from argon2 import PasswordHasher, exceptions as argon_exc
import pyotp

DB_PATH = os.environ.get("BEDMGMT_AUTH_DB", "auth.db")
PEPPER = os.environ.get("BEDMGMT_PEPPER", "")

ph = PasswordHasher(time_cost=3, memory_cost=64_000, parallelism=2)

LOCKOUT_THRESHOLD = 5
LOCKOUT_WINDOW_SEC = 15*60
LOCKOUT_DURATION_SEC = 15*60
PASSWORD_MIN_LEN = 12
PASSWORD_MAX_LEN = 128

@dataclass
class User:
    id: int
    username: str
    password_hash: str
    mfa_secret: Optional[str]
    is_active: bool
    failed_attempts: int
    last_failed_at: Optional[int]
    locked_until: Optional[int]
    created_at: int

def _conn() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON;")
    return con

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  mfa_secret TEXT,
  is_active INTEGER NOT NULL DEFAULT 1,
  failed_attempts INTEGER NOT NULL DEFAULT 0,
  last_failed_at INTEGER,
  locked_until INTEGER,
  created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS roles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS permissions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS role_permissions (
  role_id INTEGER NOT NULL,
  permission_id INTEGER NOT NULL,
  PRIMARY KEY (role_id, permission_id),
  FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
  FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_roles (
  user_id INTEGER NOT NULL,
  role_id INTEGER NOT NULL,
  PRIMARY KEY (user_id, role_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  action TEXT NOT NULL,
  resource TEXT,
  ts INTEGER NOT NULL,
  meta TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_log(ts);
"""

def init_db() -> None:
    with _conn() as c:
        c.executescript(SCHEMA_SQL)

def _now() -> int:
    return int(time.time())

def generate_password(length: int = 16) -> str:
    if length < PASSWORD_MIN_LEN or length > PASSWORD_MAX_LEN:
        length = 16
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*+-_=!"
    return "".join(secrets.choice(alphabet) for _ in range(length))

def _hash_password(raw_password: str) -> str:
    return ph.hash(raw_password + PEPPER)

def _verify_password(stored_hash: str, raw_password: str) -> bool:
    try:
        return ph.verify(stored_hash, raw_password + PEPPER)
    except argon_exc.VerifyMismatchError:
        return False
    except argon_exc.VerificationError:
        return False

def _password_policy_ok(pw: str) -> Tuple[bool, List[str]]:
    issues = []
    if not (PASSWORD_MIN_LEN <= len(pw) <= PASSWORD_MAX_LEN):
        issues.append(f"Length must be {PASSWORD_MIN_LEN}-{PASSWORD_MAX_LEN}.")
    if sum(ch.islower() for ch in pw) < 1: issues.append("Add a lowercase letter.")
    if sum(ch.isupper() for ch in pw) < 1: issues.append("Add an uppercase letter.")
    if sum(ch.isdigit() for ch in pw) < 1: issues.append("Add a digit.")
    specials = set("@#$%&*+-_=!")
    if sum(ch in specials for ch in pw) < 1: issues.append("Add a special (@#$%&*+-_=!).")
    if " " in pw: issues.append("No spaces allowed.")
    return (len(issues) == 0, issues)

def ensure_role(name: str) -> int:
    with _conn() as c:
        c.execute("INSERT OR IGNORE INTO roles(name) VALUES(?)", (name,))
        rid = c.execute("SELECT id FROM roles WHERE name=?", (name,)).fetchone()[0]
        return rid

def ensure_permission(name: str) -> int:
    with _conn() as c:
        c.execute("INSERT OR IGNORE INTO permissions(name) VALUES(?)", (name,))
        pid = c.execute("SELECT id FROM permissions WHERE name=?", (name,)).fetchone()[0]
        return pid

def grant_role_permission(role: str, permission: str) -> None:
    rid = ensure_role(role)
    pid = ensure_permission(permission)
    with _conn() as c:
        c.execute("INSERT OR IGNORE INTO role_permissions(role_id, permission_id) VALUES (?,?)", (rid, pid))

def assign_user_roles(username: str, roles):
    with _conn() as c:
        row = c.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
        if not row:
            raise ValueError("User not found")
        uid = row[0]
        for r in roles:
            rid = ensure_role(r)
            c.execute("INSERT OR IGNORE INTO user_roles(user_id, role_id) VALUES (?,?)", (uid, rid))

def user_has_permission(user_id: int, permission: str) -> bool:
    with _conn() as c:
        row = c.execute("""
            SELECT 1
            FROM user_roles ur
            JOIN roles r ON r.id = ur.role_id
            JOIN role_permissions rp ON rp.role_id = r.id
            JOIN permissions p ON p.id = rp.permission_id
            WHERE ur.user_id = ? AND p.name = ?
            LIMIT 1
        """, (user_id, permission)).fetchone()
        return bool(row)

def create_user(username: str, raw_password: Optional[str] = None, enable_mfa: bool = False, roles=()) -> Tuple[str, Optional[str]]:
    if not username or username.strip() == "":
        raise ValueError("Username required")
    with _conn() as c:
        if c.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
            raise ValueError("Username already exists")

    if raw_password is None:
        raw_password = generate_password(16)
    ok, issues = _password_policy_ok(raw_password)
    if not ok:
        raise ValueError("Password policy: " + "; ".join(issues))

    mfa_secret = pyotp.random_base32() if enable_mfa else None
    pwd_hash = _hash_password(raw_password)
    ts = _now()
    with _conn() as c:
        c.execute("""
            INSERT INTO users(username, password_hash, mfa_secret, is_active, created_at)
            VALUES (?,?,?,?,?)
        """, (username, pwd_hash, mfa_secret, 1, ts))
    if roles:
        assign_user_roles(username, roles)

    if enable_mfa:
        totp = pyotp.TOTP(mfa_secret)
        provisioning_uri = totp.provisioning_uri(name=username, issuer_name="BedMgmt")
        return raw_password, provisioning_uri
    return raw_password, None

def rotate_password(username: str, new_password: str) -> None:
    ok, issues = _password_policy_ok(new_password)
    if not ok:
        raise ValueError("Password policy: " + "; ".join(issues))
    with _conn() as c:
        c.execute("UPDATE users SET password_hash=? WHERE username=?", (_hash_password(new_password), username))

def set_user_active(username: str, active: bool) -> None:
    with _conn() as c:
        c.execute("UPDATE users SET is_active=? WHERE username=?", (1 if active else 0, username))

def fetch_user(username: str) -> Optional[User]:
    with _conn() as c:
        row = c.execute("""
            SELECT id, username, password_hash, mfa_secret, is_active, failed_attempts, last_failed_at, locked_until, created_at
            FROM users WHERE username=?
        """, (username,)).fetchone()
    if not row:
        return None
    return User(*row)

def audit(user_id: Optional[int], action: str, resource: Optional[str] = None, meta: Optional[dict] = None) -> None:
    with _conn() as c:
        c.execute("""
            INSERT INTO audit_log(user_id, action, resource, ts, meta)
            VALUES (?,?,?,?,?)
        """, (user_id, action, resource, _now(), json.dumps(meta or {})))

def _register_failure(u: User) -> None:
    now = _now()
    with _conn() as c:
        failed = u.failed_attempts + 1 if (u.last_failed_at and now - u.last_failed_at <= LOCKOUT_WINDOW_SEC) else 1
        locked_until = u.locked_until
        if failed >= LOCKOUT_THRESHOLD:
            locked_until = now + LOCKOUT_DURATION_SEC
        c.execute("""
            UPDATE users
            SET failed_attempts=?, last_failed_at=?, locked_until=?
            WHERE id=?
        """, (failed, now, locked_until, u.id))

def _reset_failures(u: User) -> None:
    with _conn() as c:
        c.execute("UPDATE users SET failed_attempts=0, last_failed_at=NULL, locked_until=NULL WHERE id=?", (u.id,))

def authenticate(username: str, raw_password: str, totp_code: Optional[str] = None) -> Tuple[bool, Optional[int], str]:
    u = fetch_user(username)
    if not u:
        audit(None, "auth_failure", resource="login", meta={"reason":"unknown_user","username":username})
        try: ph.verify(ph.hash("dummy"+PEPPER), raw_password + PEPPER)
        except Exception: pass
        return False, None, "Invalid credentials."

    now = _now()
    if not u.is_active:
        audit(u.id, "auth_failure", resource="login", meta={"reason":"inactive"})
        return False, None, "Account disabled. Contact admin."

    if u.locked_until and now < u.locked_until:
        wait = u.locked_until - now
        audit(u.id, "auth_failure", resource="login", meta={"reason":"locked","wait_sec":wait})
        return False, None, f"Account locked. Try again in {wait//60} min."

    if not _verify_password(u.password_hash, raw_password):
        _register_failure(u)
        audit(u.id, "auth_failure", resource="login", meta={"reason":"bad_password"})
        return False, None, "Invalid credentials."

    if u.mfa_secret:
        if not totp_code:
            audit(u.id, "auth_failure", resource="login", meta={"reason":"mfa_required"})
            return False, None, "MFA code required."
        totp = pyotp.TOTP(u.mfa_secret)
        if not totp.verify(totp_code, valid_window=1):
            _register_failure(u)
            audit(u.id, "auth_failure", resource="login", meta={"reason":"bad_totp"})
            return False, None, "Invalid MFA code."

    _reset_failures(u)
    audit(u.id, "auth_success", resource="login")
    return True, u.id, "Login successful."

def require_permission(user_id: int, permission: str) -> bool:
    allowed = user_has_permission(user_id, permission)
    audit(user_id, "authz_check", resource=permission, meta={"allowed": allowed})
    return allowed

def bootstrap_defaults():
    init_db()
    for p in [
        "beds.view", "beds.assign", "beds.discharge",
        "patients.view", "patients.edit",
        "reports.view", "admin.users", "admin.roles"
    ]:
        ensure_permission(p)

    nurse = "nurse"; ensure_role(nurse)
    for p in ["beds.view","beds.assign","beds.discharge","patients.view"]:
        grant_role_permission(nurse, p)

    clerk = "clerk"; ensure_role(clerk)
    for p in ["beds.view","patients.view","patients.edit"]:
        grant_role_permission(clerk, p)

    admin = "admin"; ensure_role(admin)
    for p in ["beds.view","beds.assign","beds.discharge","patients.view","patients.edit","reports.view","admin.users","admin.roles"]:
        grant_role_permission(admin, p)

    if not fetch_user("admin"):
        pw, uri = create_user("admin", raw_password=generate_password(20), enable_mfa=True, roles=[admin])
        print("[INIT] Admin username: admin")
        print("[INIT] Admin password:", pw)
        if uri:
            print("[INIT] Scan this MFA URI with an authenticator app:\n", uri)
