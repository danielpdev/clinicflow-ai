"""Reproducible browser acceptance: actual API-backed interactions plus mobile layout."""
import asyncio
import os
import socket
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    assert Path('web/dist/index.html').exists(),'Run make web-setup web-build first'
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    with tempfile.TemporaryDirectory() as directory:
        env=dict(os.environ,DATABASE_URL='sqlite:///'+str(Path(directory)/'browser.sqlite'))
        with open(Path(directory)/'server.log','w') as log:
            proc=subprocess.Popen([sys.executable,'-m','uvicorn','app.api:app','--host','127.0.0.1','--port',str(port)],env=env,stdout=log,stderr=log)
            try:
                for _ in range(100):
                    try:urllib.request.urlopen(f'http://127.0.0.1:{port}/openapi.json',timeout=1);break
                    except Exception:await asyncio.sleep(.1)
                async with async_playwright() as p:
                    browser=await p.chromium.launch()
                    page=await browser.new_page(viewport={'width':1440,'height':1000})
                    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                    await page.goto(f'http://127.0.0.1:{port}')
                    await page.get_by_role('heading',level=1).wait_for()
                    await page.get_by_role('button',name='Select',exact=True).first.click()
                    await page.get_by_label('I confirm the selected').check()
                    await page.get_by_role('button',name='Confirm appointment',exact=True).click()
                    await page.get_by_text('Booking confirmed: slot-1').wait_for()
                    assert await page.get_by_role('button',name='Booked',exact=True).count()==1
                    await page.set_viewport_size({'width':390,'height':844})
                    assert await page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),'mobile overflow'
                    assert not errors,errors
                    await browser.close()
                    print('Desktop interaction and mobile layout: PASS')
            finally:
                proc.terminate()
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.kill();proc.wait()

if __name__=='__main__':asyncio.run(main())
