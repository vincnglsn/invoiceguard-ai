"""
InvoiceGuard AI -- Helpers de navigation multipage.

Les pages clientes (application, onboarding, tarifs, guide, mentions legales)
sont declarees dans streamlit_app.py via st.navigation. Chaque script reste
toutefois lancable seul (`streamlit run invoiceguard_pricing.py`) pour le
developpement local : dans ce cas st.page_link / st.switch_page echouent, et on
retombe sur un lien HTTP vers le port local du script (cf. auto_startup.py).
"""

import streamlit as st
from streamlit.errors import StreamlitAPIException

# Ports utilises quand les scripts tournent en autonome (voir auto_startup.py
# et START_INVOICEGUARD.bat). Sert uniquement de repli hors mode multipage.
PORTS_LOCAUX = {
    "invoiceguard_app.py": 8502,
    "invoiceguard_pricing.py": 8507,
    "invoiceguard_guide.py": 8509,
}


def url_locale(script: str) -> str | None:
    """URL du script quand il tourne en autonome, ou None si inconnu."""
    port = PORTS_LOCAUX.get(script)
    return f"http://localhost:{port}" if port else None


def lien_page(script: str, label: str, icon: str | None = None,
              primary: bool = False) -> None:
    """Affiche un lien vers une autre page de l'app.

    En mode multipage : st.page_link. En autonome : bouton vers le port local.
    """
    try:
        st.page_link(script, label=label, icon=icon, use_container_width=True)
        return
    except StreamlitAPIException:
        pass

    url = url_locale(script)
    if url:
        st.link_button(label, url, use_container_width=True,
                       type="primary" if primary else "secondary")


def aller_vers(script: str) -> None:
    """Navigue vers une autre page de l'app.

    st.switch_page leve une RerunException en cas de succes : on ne rattrape
    que StreamlitAPIException (page inconnue = mode autonome).
    """
    try:
        st.switch_page(script)
    except StreamlitAPIException:
        url = url_locale(script)
        if url:
            st.info(f"Ouvrez cette page ici : {url}")
        else:
            st.warning(f"Page indisponible en mode autonome : {script}")
