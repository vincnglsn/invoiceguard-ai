"""
InvoiceGuard AI — Persistance SQLite
Sauvegarde les factures, relances et utilisateurs entre les sessions.
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "invoiceguard.db")


def _get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crée les tables si elles n'existent pas."""
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            email       TEXT    UNIQUE NOT NULL,
            nom         TEXT    NOT NULL,
            societe     TEXT,
            plan        TEXT    DEFAULT 'trial',
            trial_start TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS factures (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            numero_facture  TEXT,
            client          TEXT,
            montant         REAL,
            date_emission   TEXT,
            date_echeance   TEXT,
            statut          TEXT    DEFAULT 'En attente',
            email_client    TEXT,
            telephone       TEXT,
            date_paiement   TEXT,
            created_at      TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS relances (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            facture_id      INTEGER,
            client          TEXT,
            canal           TEXT,
            ton             TEXT,
            sujet           TEXT,
            corps           TEXT,
            date_envoi      TEXT    DEFAULT (datetime('now')),
            succes          INTEGER DEFAULT 0,
            message_id      TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS leads (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            email       TEXT    UNIQUE NOT NULL,
            nom         TEXT,
            societe     TEXT,
            telephone   TEXT,
            ca_estime   REAL,
            source      TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


# ─── Users ────────────────────────────────────────────────────────────────────

def upsert_user(email: str, nom: str, societe: str = "", plan: str = "trial") -> int:
    conn = _get_conn()
    existing = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
    if existing:
        conn.close()
        return existing["id"]
    conn.execute(
        "INSERT INTO users (email, nom, societe, plan, trial_start) VALUES (?,?,?,?,?)",
        (email, nom, societe, plan, datetime.now().isoformat())
    )
    conn.commit()
    uid = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()["id"]
    conn.close()
    return uid


def get_user(email: str) -> dict:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    return dict(row) if row else {}


def get_all_users() -> pd.DataFrame:
    conn = _get_conn()
    df = pd.read_sql("SELECT * FROM users ORDER BY created_at DESC", conn)
    conn.close()
    return df


# ─── Factures ─────────────────────────────────────────────────────────────────

def save_factures(user_id: int, df: pd.DataFrame):
    """Sauvegarde (remplace) les factures d'un utilisateur."""
    conn = _get_conn()
    conn.execute("DELETE FROM factures WHERE user_id=?", (user_id,))
    for _, row in df.iterrows():
        conn.execute("""
            INSERT INTO factures
              (user_id, numero_facture, client, montant, date_emission, date_echeance, statut, email_client, telephone)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            user_id,
            str(row.get("numero_facture", "")),
            str(row.get("client", "")),
            float(row.get("montant", 0)),
            str(row.get("date_emission", ""))[:10],
            str(row.get("date_echeance", ""))[:10],
            str(row.get("statut", "En attente")),
            str(row.get("email_client", "")),
            str(row.get("telephone", "")),
        ))
    conn.commit()
    conn.close()


def load_factures(user_id: int) -> pd.DataFrame:
    conn = _get_conn()
    df = pd.read_sql("SELECT * FROM factures WHERE user_id=? ORDER BY date_echeance", conn, params=(user_id,))
    conn.close()
    if df.empty:
        return df
    df["date_echeance"] = pd.to_datetime(df["date_echeance"], errors="coerce")
    df["date_emission"] = pd.to_datetime(df["date_emission"], errors="coerce")
    return df


def marquer_payee(user_id: int, numero_facture: str, date_paiement: str):
    conn = _get_conn()
    conn.execute(
        "UPDATE factures SET statut='Payée', date_paiement=? WHERE user_id=? AND numero_facture=?",
        (date_paiement, user_id, numero_facture)
    )
    conn.commit()
    conn.close()


# ─── Relances ─────────────────────────────────────────────────────────────────

def save_relance(user_id: int, client: str, canal: str, ton: str,
                 sujet: str, corps: str, succes: bool, message_id: str = ""):
    conn = _get_conn()
    conn.execute("""
        INSERT INTO relances (user_id, client, canal, ton, sujet, corps, succes, message_id)
        VALUES (?,?,?,?,?,?,?,?)
    """, (user_id, client, canal, ton, sujet, corps, 1 if succes else 0, message_id))
    conn.commit()
    conn.close()


def get_relances(user_id: int) -> pd.DataFrame:
    conn = _get_conn()
    df = pd.read_sql(
        "SELECT * FROM relances WHERE user_id=? ORDER BY date_envoi DESC LIMIT 100",
        conn, params=(user_id,)
    )
    conn.close()
    return df


# ─── Leads ────────────────────────────────────────────────────────────────────

def save_lead(email: str, nom: str = "", societe: str = "",
              telephone: str = "", ca_estime: float = 0, source: str = "landing") -> bool:
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO leads (email, nom, societe, telephone, ca_estime, source) VALUES (?,?,?,?,?,?)",
            (email, nom, societe, telephone, ca_estime, source)
        )
        conn.commit()
        saved = conn.total_changes > 0
    except Exception:
        saved = False
    conn.close()
    return saved


def get_leads() -> pd.DataFrame:
    conn = _get_conn()
    df = pd.read_sql("SELECT * FROM leads ORDER BY created_at DESC", conn)
    conn.close()
    return df


# ─── Stats fondateur ──────────────────────────────────────────────────────────

def get_founder_stats() -> dict:
    conn = _get_conn()
    users = conn.execute("SELECT COUNT(*) as n FROM users").fetchone()["n"]
    leads = conn.execute("SELECT COUNT(*) as n FROM leads").fetchone()["n"]
    relances_total = conn.execute("SELECT COUNT(*) as n FROM relances").fetchone()["n"]
    relances_ok = conn.execute("SELECT COUNT(*) as n FROM relances WHERE succes=1").fetchone()["n"]
    conn.close()
    return {
        "total_users": users,
        "total_leads": leads,
        "total_relances": relances_total,
        "relances_ok": relances_ok,
        "taux_succes_relances": relances_ok / relances_total * 100 if relances_total > 0 else 0,
    }


# Init au démarrage
init_db()
