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
            page.get_by_label('Alias', exact=True).fill('Draft alias')
            page.get_by_label('Follow-Up Date', exact=True).fill('invalid-date')
            page.get_by_role('button', name='Save', exact=True).click()
            expect(page.locator('#form-error')).to_be_visible()
            expect(page.get_by_label('Alias', exact=True)).to_have_value('Draft alias')
            page.get_by_label('Follow-Up Date', exact=True).fill('2030-10-04')
            page.route('**/api/people/*', lambda route: route.abort() if route.request.method == 'PATCH' else route.continue_())
            page.get_by_role('button', name='Save', exact=True).click()
            expect(page.locator('#form-error')).to_contain_text('fetch')
            expect(page.get_by_label('Alias', exact=True)).to_have_value('Draft alias')
            page.unroute('**/api/people/*')
            page.get_by_role('button', name='Save', exact=True).click()
            expect(page.locator('#modal')).to_have_class('modal hidden')

            page.locator('[data-section-action="edit"]').first.click()
            page.get_by_label('Section text', exact=True).fill('Updated first line.\nSecond line retained.')
            page.get_by_role('button', name='Save', exact=True).click()
            expect(page.locator('#modal')).to_have_class('modal hidden')
            page.locator('[data-section-action="append"]').first.click()
            page.get_by_label('Addition', exact=True).fill('A later observation.')
            page.get_by_role('button', name='Save', exact=True).click()
            expect(page.locator('#content')).to_contain_text('A later observation.')
            page.locator('[data-section-action="history"]').first.click()
            expect(page.locator('#modal-form')).to_contain_text('First line.')
            page.get_by_role('button', name='Cancel', exact=True).click()

            page.get_by_role('button', name='Timeline', exact=True).click()
            page.get_by_role('button', name='+ New Interaction', exact=True).click()
            expect(page.get_by_label('Rowan Quinn · Fictional Makers Guild', exact=True)).to_be_checked()
            page.get_by_label('Search participants', exact=True).fill('Morgan')
            page.get_by_label('Morgan Ellis', exact=False).check()
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
            page.get_by_label('Custom relationship type', exact=True).fill('collaborator')
            page.get_by_role('button', name='Create type', exact=True).click()
            expect(page.get_by_label('Relationship Type', exact=True)).to_have_value('collaborator')
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


def test_casefile_controls_and_independent_relationships(tmp_path):
    from playwright.sync_api import sync_playwright, expect
    from PIL import Image
    from netops.gui.server import NetOpsGuiServer
    from netops.services.app_backend import NetworkOpsBackend
    from netops.storage import NetOpsRepository, connect

    db = tmp_path / 'casefiles.sqlite3'
    b = NetworkOpsBackend(NetOpsRepository(connect(db)))
    person = b.create_person({'name':'Fictional Avery','dossier':'# Background\n**Known** context'})
    other = b.create_person({'name':'Fictional Morgan'})
    common = dict(source_person_id=person['person_id'],target_person_id=other['person_id'])
    friend = b.add_relationship_link({**common,'relationship_type':'Friend','started_on':'2025-01'})
    coworker = b.add_relationship_link({**common,'relationship_type':'Coworker','started_on':'2024-09'})
    b.repository.connection.close()
    photo = tmp_path / 'portrait.png'; Image.new('RGB',(25,40),'green').save(photo)
    server = NetOpsGuiServer(backend_factory=lambda: NetworkOpsBackend(NetOpsRepository(connect(db))))
    server.start_background()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel='msedge' if sys.platform == 'win32' else None)
            page = browser.new_page(viewport={'width':1440,'height':1000}, timezone_id='Pacific/Honolulu')
            page.goto(server.url)
            page.locator('[data-view="interactions"]').click()
            page.get_by_role('button',name='+ New Interaction',exact=True).click()
            expect(page.locator('[name="participants"]:checked')).to_have_count(0)
            assert page.get_by_label('Date',exact=True).input_value() == page.evaluate('localToday()')
            page.get_by_role('button',name='Cancel',exact=True).click()
            page.locator('[data-view="people"]').click()
            page.get_by_role('button',name='Fictional Avery',exact=False).click()
            expect(page.locator('.document-body strong')).to_have_text('Known')
            page.get_by_role('button',name='Change photo',exact=True).click()
            page.locator('#photo-file').set_input_files(str(photo))
            expect(page.locator('#photo-preview')).to_be_visible()
            page.get_by_role('button',name='Save',exact=True).click()
            expect(page.locator('#modal')).to_have_class('modal hidden')
            expect(page.locator('.avatar-large img')).to_be_visible()
            page.get_by_role('button',name='Edit Person',exact=True).click()
            page.get_by_label('New tag name',exact=True).fill('Research Club')
            page.get_by_role('button',name='Create tag',exact=True).click()
            expect(page.get_by_label('Research Club',exact=True)).to_be_checked()
            page.get_by_role('button',name='Save',exact=True).click()
            expect(page.locator('.assigned-tags')).to_contain_text('Research Club')
            page.locator('[data-tab="connections"]').click()
            page.locator(f'[data-end-relationship="{friend["id"]}"]').click()
            page.get_by_label('Ended (optional)',exact=True).fill('2025-09')
            page.get_by_role('button',name='Save',exact=True).click()
            expect(page.locator(f'[data-relationship-id="{friend["id"]}"]')).to_contain_text('Ended')
            expect(page.locator(f'[data-relationship-id="{coworker["id"]}"]')).to_contain_text('Active')
            page.get_by_role('button',name='+ New Relationship',exact=True).click()
            page.get_by_label('Target Person',exact=True).select_option(other['person_id'])
            page.get_by_label('Relationship Type',exact=True).select_option('Friend')
            page.get_by_label('Started (YYYY-MM or YYYY-MM-DD)',exact=True).fill('2026-01')
            page.get_by_role('button',name='Save',exact=True).click()
            expect(page.locator('.relationship-record')).to_have_count(3)
            page.locator('[data-tab="signals"]').click()
            page.get_by_role('button',name='+ New Intel',exact=True).click()
            page.get_by_label('Information',exact=True).fill('Provisional interpretation')
            page.get_by_label('Intel type',exact=True).select_option('Inference')
            page.get_by_label('Event date',exact=True).fill('2023-04-05')
            page.get_by_role('button',name='Save',exact=True).click()
            expect(page.locator('#modal')).to_have_class('modal hidden')
            page.get_by_role('button',name='Edit Intel',exact=True).click()
            page.get_by_label('Information',exact=True).fill('Corrected interpretation')
            page.get_by_role('button',name='Save',exact=True).click()
            expect(page.locator('#content')).to_contain_text('Corrected interpretation')
            page.get_by_role('button',name='History',exact=True).click()
            expect(page.locator('#modal-form')).to_contain_text('Provisional interpretation')
            page.get_by_role('button',name='Cancel',exact=True).click()
            page.locator('[data-tab="interactions"]').click()
            expect(page.locator('#content')).to_contain_text('Friend ended')
            expect(page.locator('#content')).to_contain_text('2023-04-05')
            page.reload()
            page.locator('[data-view="tags"]').click()
            expect(page.locator('#content')).to_contain_text('Research Club')
            expect(page.locator('#content')).to_contain_text('1 people')
            browser.close()
    finally:
        server.stop()
