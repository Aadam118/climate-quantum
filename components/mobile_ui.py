"""
components/mobile_ui.py
------------------------
Small JS injection that force-closes the sidebar on mobile right after the
user taps "Run Quantum Inference", so the prediction result is immediately
visible instead of being hidden behind the open sidebar.
"""

import time
import streamlit.components.v1 as components


def close_sidebar_on_mobile():
    components.html(
        f"""
        <script>
            // 500ms delay so this fires after the spinner has mounted
            setTimeout(() => {{
                const doc = window.parent.document;

                // Trick 1: dispatch an 'Escape' keypress (most reliable on mobile)
                doc.dispatchEvent(new KeyboardEvent('keydown', {{'key': 'Escape', 'bubbles': true}}));

                // Trick 2: click the background overlay outside the sidebar
                const appContainer = doc.querySelector('[data-testid="stAppViewContainer"]');
                if (appContainer) {{
                    appContainer.click();
                }}
            }}, 500);
        </script>
        <div style="display:none;">{time.time()}</div>
        """,
        height=0,
        width=0,
    )
