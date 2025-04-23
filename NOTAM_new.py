import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import fitz  # PyMuPDF for PDF parsing
from datetime import datetime


def download_pdf(url, download_dir):
    options = Options()
    options.headless = True  # Enable headless mode
    options.add_argument("--headless")
    
    # Auto-download PDFs without prompting
    options.set_preference("browser.download.dir", download_dir)
    options.set_preference("browser.download.folderList", 2)  # Use custom directory
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
    options.set_preference("pdfjs.disabled", True)  # Disable built-in PDF viewer (forces download)

    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

    try:
        driver.get(url)
        print("Navigated to:", url)

        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))

        # Find and click the NOTAM PDF link
        pdf_link_xpath = "/html/body/cache/main/div[2]/div/div/div/article/a"
        download_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, pdf_link_xpath))
        )
        driver.execute_script("arguments[0].click();", download_link)
        print("Clicked the NOTAM link.")

        # Wait for the new tab and switch to it (the PDF viewer)
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
        driver.switch_to.window(driver.window_handles[1])

        # Wait for the download button to be present and click it via JavaScript
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "downloadButton")))
        driver.execute_script('document.getElementById("downloadButton").click();')
        print("Clicked the download button via JavaScript")

        # Wait for file download
        time.sleep(5)

        # Verify if the PDF was downloaded by listing files in the download directory.
        files = sorted(os.listdir(download_dir), key=lambda x: os.path.getmtime(os.path.join(download_dir, x)))
        if files:
            pdf_file = os.path.join(download_dir, files[-1])
            print("PDF downloaded:", pdf_file)
            return True, pdf_file
        else:
            print("No PDF file found.")
            return False, None

    except Exception as e:
        print("Error during download:", e)
        return False, None
    finally:
        driver.quit()


def extract_todays_notams(download_dir, output_txt):
    # Scan the downloads directory for a PDF file whose name starts with "PIB" (case-insensitive)
    print("Scanning download directory for a PDF starting with 'PIB'...")
    files = os.listdir(download_dir)
    pdf_files = [f for f in files if f.lower().endswith('.pdf') and f.upper().startswith("PIB")]
    if not pdf_files:
        print("No PDF file found in", download_dir, "with a name starting with 'PIB'.")
        return
    pdf_files = sorted(pdf_files, key=lambda x: os.path.getmtime(os.path.join(download_dir, x)))
    pdf_path = os.path.join(download_dir, pdf_files[-1])
    print("Found PDF file for extraction:", pdf_path)

    try:
        pdf_document = fitz.open(pdf_path)
        if pdf_document.page_count == 0:
            raise RuntimeError("The downloaded PDF is empty or invalid.")

        # Today's date in "DD MMM YYYY" format (e.g., "04 APR 2025")
        today_date = datetime.today().strftime('%d %b %Y').upper()
        print(f"Searching for NOTAMs with validity date: {today_date}")

        extracted_notams = []
        current_block = []  # Accumulate lines for the current NOTAM block

        # Gather all lines from all pages into one list.
        all_lines = []
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            all_lines.extend(page.get_text("text").split("\n"))

        # Ignore all text before the marker "EISN - SHANNON FIR"
        start_index = 0
        for i, line in enumerate(all_lines):
            if "EISN - SHANNON FIR" in line:
                start_index = i
                break
        all_lines = all_lines[start_index:]
        print("Ignored text before 'EISN - SHANNON FIR'")

        # Process each line to form blocks delimited by a line starting with "+"
        for line in all_lines:
            # Stop processing if the stop marker is encountered.
            if "EGGX - SHANWICK OCEANIC FIR" in line:
                break

            if line.lstrip().startswith("+"):
                if current_block:
                    block_text = " ".join(current_block)
                    if today_date in block_text:
                        extracted_notams.append("\n".join(current_block))
                    current_block = []
                current_block.append(line)
            else:
                current_block.append(line)

        if current_block:
            block_text = " ".join(current_block)
            if today_date in block_text:
                extracted_notams.append("\n".join(current_block))

        if extracted_notams:
            with open(output_txt, "w", encoding="utf-8") as f:
                f.write("\n\n".join(extracted_notams))
            print(f"Filtered NOTAMs saved to {output_txt}")
        else:
            print("No NOTAMs found for today's date.")

        pdf_document.close()
        os.remove(pdf_path)
        print("Cleaned up PDF file.")

    except Exception as e:
        print("Error processing PDF:", e)


if __name__ == "__main__":
    url = "https://www.airnav.ie/air-traffic-management/notam-notice-to-airmen-24e348473e7b0153452e634c36c72213"
    download_dir = r'C:\Users\Nathaniel\Downloads'
    output_txt = r'C:\Users\Nathaniel\Downloads\filtered_notams.txt'

    # Download the PDF.
    success, _ = download_pdf(url, download_dir)
    # Then extract NOTAMs from the PDF found in the downloads directory.
    extract_todays_notams(download_dir, output_txt)

