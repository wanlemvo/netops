"""Run with NETOPS_BROWSER_TESTS=1; only fictional temporary data is used."""
import os
from pathlib import Path
import sys

import pytest

pytestmark = pytest.mark.skipif(os.environ.get('NETOPS_BROWSER_TESTS') != '1', reason='Opt-in real browser workflow')


def test_complete_gui_workflow(tmp_path):
    from playwright.sync_api import sync_playwright, expect
    from netops.demo import seed_demo
    from netops.gui.server import NetOpsGuiServer
    from netops.services.app_backend import NetworkOpsBackend
    from netops.storage import NetOpsRepository, connect

    db = tmp_path / 'fictional.sqlite3'
    seed_demo(db)
    server = NetOpsGuiServer(backend_factory=lambda: NetworkOpsBackend(NetOpsRepository(connect(db))))
    server.start_background()
    output = Path(os.environ.get('NETOPS_CAPTURE_DIR', str(tmp_path / 'capture'))).resolve()
    output.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel='msedge' if sys.platform == 'win32' else None)
            context = browser.new_context(viewport={'width': 1440, 'height': 1000}, record_video_dir=str(output / 'recordings'))
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(server.url)
            expect(page.locator('#people-list')).to_have_count(0)
            page.locator('[data-view="people"]').click()
            expect(page.locator('#people-list .person-row')).to_have_count(2)
            page.screenshot(path=str(output / 'dashboard.png'), full_page=True)
            page.get_by_role('button', name='Avery Chen', exact=False).click()
            expect(page.get_by_role('heading', name='Avery Chen', exact=True)).to_be_visible()
            page.screenshot(path=str(output / 'dossier.png'), full_page=True)

            # Filtered creation must open the new person, independent of alphabetical order.
            page.get_by_role('button', name='Back to People', exact=False).click()
            page.locator('#directory-search').fill('no matching person')
            expect(page.locator('#people-list .person-row')).to_have_count(0)
            page.get_by_role('button', name='+ New Person', exact=True).click()
            page.get_by_label('Name', exact=True).fill('Rowan Quinn')
            page.get_by_label('Organization', exact=True).fill('Fictional Makers Guild')
            page.get_by_label('Dossier', exact=True).fill('First line.\nSecond line.')
            page.get_by_role('button', name='Save', exact=True).click()
            expect(page.get_by_role('heading', name='Rowan Quinn', exact=True)).to_be_visible()
            expect(page.locator('#people-list')).to_have_count(0)

            page.get_by_role('button', name='Edit Person', exact=True).click()
            page.get_by_label('Dossier', exact=True).fill('Updated first line.\nSecond line retained.')
            page.get_by_label('Follow-Up Date', exact=True).fill('invalid-date')
            page.get_by_role('button', name='Save', exact=True).click()
            expect(page.locator('#form-error')).to_be_visible()
            expect(page.get_by_label('Dossier', exact=True)).to_have_value('Updated first line.\nSecond line retained.')
            page.get_by_label('Follow-Up Date', exact=True).fill('2030-10-04')
            page.route('**/api/people/*', lambda route: route.abort() if route.request.method == 'PATCH' else route.continue_())
            page.get_by_role('button', name='Save', exact=True).click()
            expect(page.locator('#form-error')).to_contain_text('fetch')
            expect(page.get_by_label('Dossier', exact=True)).to_have_value('Updated first line.\nSecond line retained.')
            page.unroute('**/api/people/*')
            page.get_by_role('button', name='Save', exact=True).click()
            expect(page.locator('#modal')).to_have_class('modal hidden')

            page.get_by_role('button', name='Timeline', exact=True).click()
            page.get_by_role('button', name='+ New Interaction', exact=True).click()
            page.get_by_label('Summary', exact=True).fill('Agreed on a fictional project outline.')
            page.get_by_label('Follow-Up Date', exact=True).fill('2030-10-05')
            page.get_by_role('button', name='Save', exact=True).click()
            expect(page.locator('#modal')).to_have_class('modal hidden')
            expect(page.locator('#content')).to_contain_text('Agreed on a fictional project outline.')
            page.get_by_role('button', name='Complete follow-up', exact=True).click()
            expect(page.locator('#content')).to_contain_text('Follow-up completed')

            for tab, add, values, expected in [
                ('Contact', '+ New Contact', {'Value': 'rowan@example.com'}, 'rowan@example.com'),
                ('Signals', '+ New Intel', {'Information': 'Prefers written agendas'}, 'Prefers written agendas'),
                ('Opportunities', '+ New Opportunity', {'Title': 'Fictional learning exchange'}, 'Fictional learning exchange'),
            ]:
                page.locator(f'[data-tab="{dict(Contact="contacts", Signals="signals", Opportunities="opportunities")[tab]}"]').click()
                page.get_by_role('button', name=add, exact=True).click()
                for label, value in values.items(): page.get_by_label(label, exact=True).fill(value)
                page.get_by_role('button', name='Save', exact=True).click()
                expect(page.locator('#modal')).to_have_class('modal hidden')
                expect(page.locator('#content')).to_contain_text(expected)

            page.locator('[data-tab="connections"]').click()
            page.get_by_role('button', name='+ New Relationship', exact=True).click()
            page.get_by_label('Target Person', exact=True).select_option(label='Morgan Ellis')
            page.get_by_label('Relationship Type', exact=True).fill('collaborator')
            page.get_by_role('button', name='Save', exact=True).click()
            expect(page.locator('#modal')).to_have_class('modal hidden')
            expect(page.locator('#content')).to_contain_text('Morgan Ellis')

            page.reload()
            page.locator('[data-view="people"]').click()
            page.locator('#directory-search').fill('Rowan Quinn')
            expect(page.locator('#people-list .person-row')).to_have_count(1)
            page.locator('#people-list .person-row').click()
            expect(page.locator('#content')).to_contain_text('Updated first line.')
            page.locator('[data-tab="interactions"]').click()
            expect(page.locator('#content')).to_contain_text('Follow-up completed')
            page.get_by_role('button', name='Back to People', exact=False).click()
            page.get_by_role('button', name='+ New Person', exact=True).click()
            page.get_by_label('Name', exact=True).fill('Rowan Quinn')
            page.get_by_label('Organization', exact=True).fill('Different fictional organization')
            page.get_by_role('button', name='Save', exact=True).click()
            expect(page.locator('#modal')).to_have_class('modal hidden')
            page.get_by_role('button', name='Back to People', exact=False).click()
            page.locator('#directory-search').fill('Rowan Quinn')
            expect(page.locator('#people-list .person-row')).to_have_count(2)
            page.locator('#people-list .person-row').filter(has_text='Fictional Makers Guild').click()
            expect(page.locator('#content')).to_contain_text('Updated first line.')
            # Collapsing is local layout state: no API reload, selected dossier/tab retained.
            page.locator('[data-tab="signals"]').click()
            reads = []
            page.on('request', lambda request: reads.append(request.url) if '/api/' in request.url else None)
            before = len(reads)
            page.get_by_role('button', name='Collapse navigation', exact=True).click()
            expect(page.locator('body')).to_have_class('nav-collapsed')
            expect(page.locator('[data-tab="signals"]')).to_have_class('tab active')
            assert len(reads) == before
            page.get_by_role('button', name='+ New Intel', exact=True).click()
            page.get_by_label('Information', exact=True).fill('Draft survives navigation toggle')
            page.locator('#nav-toggle').evaluate('(button) => button.click()')
            expect(page.get_by_label('Information', exact=True)).to_have_value('Draft survives navigation toggle')
            page.get_by_role('button', name='Cancel', exact=True).click()
            page.get_by_role('button', name='Collapse navigation', exact=True).click()
            page.reload()
            expect(page.locator('body')).to_have_class('nav-collapsed')
            page.locator('[data-view="signals"]').click()
            page.get_by_role('button', name='+ New Intel', exact=True).click()
            expect(page.get_by_label('Person', exact=True)).to_have_value('')
            page.get_by_role('button', name='Cancel', exact=True).click()
            for width in [1024, 1440]:
                page.set_viewport_size({'width': width, 'height': 1000})
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
            assert errors == []
            context.close()
            browser.close()
    finally:
        server.stop()
