import csv
import asyncio
import time
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import requests

#Given a csv containing all raw names and locations.
#Scrapes Fast people search using playwrite and grabs all email and phone contact info for each matching individual
#Final result will be each entry with all possible given numbers and emails.

filename = "Names/finalInput.csv"

fields = []
data = []

# Reading CSV file
with open(filename, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    fields = next(csvreader)
    for row in csvreader:
        data.append(row)

numPeople = len(data)
fields.append("Phone_Number_List")
fields.append("Email_Address_List")

for row in data:
    row.append([])  # Placeholder for phone numbers
    row.append([])  # Placeholder for emails

printingFile = open("Names/print.csv", "a")

async def scrape_numbers_emails(url, page):
    numbers = []
    emails = []

    response = await page.goto(url, timeout=9000000)
    
    #print(f"Response for {url}: {response}")

    #print(f"Response for {url}: {response}", file=printingFile)

    html_content = await page.content()
    #print(f"HTML content for {url}:\n{html_content}")
    #print(f"HTML content for {url}:\n{html_content}",file=printingFile)

    nums = await page.locator('div.detail-box-phone div.row dl.col-sm-12.col-md-6').all()
    print(len(nums))
    for num in nums:
        a_tag = await num.inner_html()  # Retrieve the inner HTML of the <a> tag within the <dl> element
        if a_tag:
            href = a_tag.split('href="')[1].split('"')[0]  # Extract the href attribute
            numbers.append(href)

    es = await page.locator('div#email_section div.detail-box-content div.detail-box-email div.row h3.col-sm-12.col-md-6').all()
    print(len(es))
    for e in es:
        emails.append(await e.text_content())


    await page.close()
    return numbers, emails

async def scrape_url(url, page):
    await page.goto(url, timeout=9000000)

    card_titles = await page.locator('h2.card-title').all()
    url_list = []
    
    for title in card_titles:
        a_tag = await title.inner_html()  # Retrieve the inner HTML of the title element
        if a_tag:
            href = a_tag.split('href="')[1].split('"')[0]
            url_list.append(href)
    
    await page.close()
    return url_list

async def process_person(row, browser):
    full_name = row[20]
    state = row[10]
    city = row[15]
    phone_numbers = []
    emails = []

    
    
    

    if '&' in full_name:
        parts = full_name.split('&')
        lastName = parts[1].split(' ')
        full_name = parts[0] + "" + lastName[2]

    print("Name!:", full_name)
    print("Name!:", full_name, file=printingFile)

    if ',' in full_name and '"' in full_name:
        parts = full_name.split(',')
        full_name = parts[1] + " " + parts[0]
        print("Cooma parse!:", full_name)
        print("Cooma parse!:", full_name, file=printingFile)

    full_name = full_name.replace('. ', ' ') 
    full_name = full_name.replace('.', ' ')  
    full_name = full_name.lower()
    full_name = full_name.replace('"', '')
    full_name = full_name.replace(', ', ' ')
    full_name = full_name.replace(',', ' ')
    

    
    url = f"https://www.fastpeoplesearch.com/name/{full_name.replace(' ', '-')}_{city.replace(' ', '-')}-{state.replace(' ', '-')}"
    #print("URL: ", url, file=printingFile)
    #print("URL: ", url)
    context = await browser.new_context()
    page = await context.new_page()

    urls = await scrape_url(url, page)

   

    print("Name, numPeopleFOund, urls", full_name, len(urls), urls , file=printingFile)
    print("Name, numPeopleFOund", full_name, len(urls))
    
    #print("URLS: ", (urls))
    async def process_batch_urls(batch_urls, cont):
        tasks = [scrape_numbers_emails(f"https://www.fastpeoplesearch.com{t}", await cont.new_page()) for t in batch_urls]
        results = await asyncio.gather(*tasks)
        for em, num in results:
            phone_numbers.extend(num)
            emails.extend(em)
    
    await context.close()

    batch_size = 4
    for i in range(0, len(urls), batch_size):
        
        newContext = await browser.new_context()
        batch_urls = urls[i:i + batch_size]
        await process_batch_urls(batch_urls, newContext)
        await newContext.close()
    #await context.close()

    row[-2] = phone_numbers
    row[-1] = emails
    return row
    

async def process_batch(batch, browser, writer):
    tasks = [process_person(row, browser) for row in batch]
    results = await asyncio.gather(*tasks)

    for result in results:
        writer.writerow(result)

async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        file1 = open("Names/Out.csv", "a", newline='')
        writer = csv.writer(file1)
        

        batch_size = 2
        startIndex = 1102
        for i in range(startIndex, numPeople, batch_size):
            print("Number: ", i, file=printingFile)
            print("Number: ", i)
            batch = data[i:i + batch_size]
            await process_batch(batch, browser, writer)
        
        await browser.close()
        file1.close()

asyncio.run(main())
