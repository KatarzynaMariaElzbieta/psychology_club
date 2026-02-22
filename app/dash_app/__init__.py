import dash_mantine_components as dmc
from dash_extensions.enrich import DashProxy

from app.cookie_texts import (
    COOKIE_ACCEPT_LABEL,
    COOKIE_BANNER_MESSAGE,
    COOKIE_REJECT_LABEL,
    COOKIE_SETTINGS_ICON,
    COOKIE_SETTINGS_LABEL,
    PRIVACY_POLICY_CONTENT,
    PRIVACY_POLICY_ICON,
    PRIVACY_POLICY_LABEL,
    PRIVACY_POLICY_TITLE,
)
from .layout import layout


def _build_ga4_snippet(measurement_id: str) -> str:
    if not measurement_id:
        return ""

    return f"""
    <style>
      .cookie-banner {{
        position: fixed;
        left: 1rem;
        right: 1rem;
        bottom: 1rem;
        z-index: 9999;
        background: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 10px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
        padding: 1rem;
        display: none;
      }}
      .cookie-banner__actions {{
        display: flex;
        gap: 0.75rem;
        margin-top: 0.75rem;
        flex-wrap: wrap;
      }}
      .cookie-banner button {{
        border: 1px solid #9ca3af;
        border-radius: 8px;
        background: #f9fafb;
        color: #111827;
        padding: 0.5rem 0.8rem;
        cursor: pointer;
      }}
      .cookie-banner button[data-action="accept"] {{
        background: #2563eb;
        border-color: #2563eb;
        color: #ffffff;
      }}
      .cookie-settings-btn {{
        width: 2.75rem;
        height: 2.75rem;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #9ca3af;
        border-radius: 999px;
        background: #ffffff;
        color: #111827;
        cursor: pointer;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
        font-size: 1.2rem;
        line-height: 1;
      }}
      .floating-policy-actions {{
        position: fixed;
        left: 1rem;
        bottom: 4.75rem;
        z-index: 9998;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
      }}
      .privacy-modal-overlay {{
        position: fixed;
        inset: 0;
        background: rgba(17, 24, 39, 0.55);
        z-index: 10000;
        display: none;
        align-items: center;
        justify-content: center;
        padding: 1rem;
      }}
      .privacy-modal {{
        width: min(760px, 100%);
        max-height: 85vh;
        overflow: auto;
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid #d1d5db;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.2);
        padding: 1rem;
      }}
      .privacy-modal__header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
      }}
      .privacy-modal__title {{
        margin: 0;
        font-size: 1.1rem;
        color: #111827;
      }}
      .privacy-modal__close {{
        border: 1px solid #9ca3af;
        background: #f9fafb;
        border-radius: 8px;
        cursor: pointer;
        padding: 0.35rem 0.55rem;
        color: #111827;
      }}
      .privacy-modal__content {{
        white-space: pre-line;
        color: #1f2937;
        line-height: 1.5;
        margin: 0;
      }}
    </style>
    <script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('consent', 'default', {{
        ad_storage: 'denied',
        analytics_storage: 'denied',
        ad_user_data: 'denied',
        ad_personalization: 'denied'
      }});
      gtag('config', '{measurement_id}', {{ send_page_view: false }});

      function hasAnalyticsConsent() {{
        return localStorage.getItem('ga4_consent') === 'granted';
      }}

      function updateConsent(granted) {{
        const state = granted ? 'granted' : 'denied';
        gtag('consent', 'update', {{
          ad_storage: 'denied',
          analytics_storage: state,
          ad_user_data: 'denied',
          ad_personalization: 'denied'
        }});
        localStorage.setItem('ga4_consent', state);
      }}

      function trackEvent(eventName, params) {{
        if (!hasAnalyticsConsent()) return;
        gtag('event', eventName, params || {{}});
      }}

      function trackPageView() {{
        trackEvent('page_view', {{
          page_location: window.location.href,
          page_path: window.location.pathname + window.location.search,
          page_title: document.title
        }});
      }}

      function hideCookieBanner() {{
        const banner = document.getElementById('cookie-banner');
        if (banner) banner.style.display = 'none';
      }}

      function showCookieBanner() {{
        const banner = document.getElementById('cookie-banner');
        if (banner) banner.style.display = 'block';
      }}

      window.acceptAnalyticsCookies = function() {{
        updateConsent(true);
        hideCookieBanner();
        trackPageView();
      }};

      window.rejectAnalyticsCookies = function() {{
        updateConsent(false);
        hideCookieBanner();
      }};

      window.openCookieSettings = function() {{
        showCookieBanner();
      }};

      window.openPrivacyPolicyModal = function() {{
        const modal = document.getElementById('privacy-modal-overlay');
        if (modal) modal.style.display = 'flex';
      }};

      window.closePrivacyPolicyModal = function() {{
        const modal = document.getElementById('privacy-modal-overlay');
        if (modal) modal.style.display = 'none';
      }};

      document.addEventListener('keydown', function(event) {{
        if (event.key === 'Escape') window.closePrivacyPolicyModal();
      }});

      function initializeConsentState() {{
        if (hasAnalyticsConsent()) {{
          updateConsent(true);
          trackPageView();
        }} else if (localStorage.getItem('ga4_consent') === 'denied') {{
          updateConsent(false);
        }} else {{
          showCookieBanner();
        }}
      }}

      if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initializeConsentState);
      }} else {{
        initializeConsentState();
      }}

      const originalPushState = history.pushState;
      history.pushState = function() {{
        originalPushState.apply(this, arguments);
        trackPageView();
      }};

      const originalReplaceState = history.replaceState;
      history.replaceState = function() {{
        originalReplaceState.apply(this, arguments);
        trackPageView();
      }};

      window.addEventListener('popstate', trackPageView);

      document.addEventListener('click', function(event) {{
        const link = event.target.closest('a');
        if (!link || !link.href) return;

        const href = link.getAttribute('href') || '';
        const host = window.location.hostname;
        const isExternal = link.hostname && link.hostname !== host;
        const isDownload = /\.(pdf|doc|docx|xls|xlsx|ppt|pptx|zip)$/i.test(href);

        if (isDownload) {{
          trackEvent('file_download', {{
            file_name: href.split('/').pop() || href,
            file_extension: (href.split('.').pop() || '').toLowerCase(),
            link_url: link.href
          }});
        }}

        if (isExternal) {{
          trackEvent('click', {{
            event_category: 'outbound',
            event_label: link.href,
            link_url: link.href
          }});
        }}
      }}, true);

      document.addEventListener('submit', function(event) {{
        const form = event.target;
        trackEvent('form_submit', {{
          form_id: form.id || '',
          form_action: form.action || window.location.pathname,
          form_method: (form.method || 'get').toLowerCase()
        }});
      }}, true);
    </script>
    """


def init_dash(flask_app):
    dash_app = DashProxy(
        __name__,
        server=flask_app,
        url_base_pathname='/',
        suppress_callback_exceptions=True,
        use_pages=True,
    )
    dash_app.title = "Studenckie Koło Psychologii WAM"
    dash_app.index_string = f"""<!DOCTYPE html>
<html lang="pl">
  <head>
    {{%metas%}}
    <title>{{%title%}}</title>
    {{%favicon%}}
    {{%css%}}
    {_build_ga4_snippet(flask_app.config.get("GA4_MEASUREMENT_ID", ""))}
  </head>
  <body>
    {{%app_entry%}}
    <div id="cookie-banner" class="cookie-banner" role="dialog" aria-live="polite">
      <div>{COOKIE_BANNER_MESSAGE}</div>
      <div class="cookie-banner__actions">
        <button type="button" data-action="accept" onclick="acceptAnalyticsCookies()">{COOKIE_ACCEPT_LABEL}</button>
        <button type="button" data-action="reject" onclick="rejectAnalyticsCookies()">{COOKIE_REJECT_LABEL}</button>
      </div>
    </div>
    <div class="floating-policy-actions">
      <button type="button" class="cookie-settings-btn" onclick="openCookieSettings()" aria-label="{COOKIE_SETTINGS_LABEL}" title="{COOKIE_SETTINGS_LABEL}">{COOKIE_SETTINGS_ICON}</button>
      <button type="button" class="cookie-settings-btn" onclick="openPrivacyPolicyModal()" aria-label="{PRIVACY_POLICY_LABEL}" title="{PRIVACY_POLICY_LABEL}">{PRIVACY_POLICY_ICON}</button>
    </div>
    <div id="privacy-modal-overlay" class="privacy-modal-overlay" onclick="if(event.target===this) closePrivacyPolicyModal()">
      <div class="privacy-modal" role="dialog" aria-modal="true" aria-labelledby="privacy-modal-title">
        <div class="privacy-modal__header">
          <h3 id="privacy-modal-title" class="privacy-modal__title">{PRIVACY_POLICY_TITLE}</h3>
          <button type="button" class="privacy-modal__close" onclick="closePrivacyPolicyModal()">Zamknij</button>
        </div>
        <p class="privacy-modal__content">{PRIVACY_POLICY_CONTENT}</p>
      </div>
    </div>
    <footer>
      {{%config%}}
      {{%scripts%}}
      {{%renderer%}}
    </footer>
  </body>
</html>"""
    dash_app.layout = dmc.MantineProvider(layout)
    return dash_app
