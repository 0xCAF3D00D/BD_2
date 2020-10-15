import xml.etree.ElementTree as ET
import pandas as pd
import re

#Инициализируем константы
VACANCY_TAG = "vacancy"
URL_TAG = "url"
MOBILE_URL_TAG = "mobile-url"
CREATION_DATE_TAG = "creation-date"
UPDATE_DATE_TAG = "update-date"
SALARY_TAG = "salary"
CURRENCY_TAG = "currency"
CATEGORY_TAG = "category"
INDUSTRY_TAG = "industry"
JOB_NAME_TAG = "job-name"
EMPLOYMENT_TAG = "employment"
SCHEDULE_TAG = "schedule"
DESCRIPTION_TAG = "description"
DUTY_TAG = "duty"
TERM_TAG = "term"
TEXT_TAG = "text"
REQUIREMENT_TAG = "requirement"
EDUCATION_TAG = "education"
QUALIFICATION_TAG = "qualification"
EXPERIENCE_TAG = "experience"
ADDRESSES_TAG = "addresses"
ADDRESS_TAG = "address"
LOCATION_TAG = "location"
METRO_TAG = "metro"
LONGTITUDE_TAG = "lng"
LATITUDE_TAG = "lat"
COMPANY_TAG = "company"
NAME_TAG = "name"
LOGO_TAG = "logo"
SITE_TAG = "site"
EMAIL_TAG = "email"
PHONE_TAG = "phone"
CONTACT_NAME_TAG = "contact-name"
HR_AGENCY_TAG = "hr-agency"

CSV_COLUMNS = [
    "url",
    "mobile-url",
    "creation_date",
    "update-date",
    "min-salary",
    "max-salary",
    "currency",
    "industry",
    "job-name",
    "employment",
    "schedule",
    "description",
    "duty",
    "term",
    "education",
    "qualification",
    "experience",
    "location",
    "longitude",
    "latitude",
    "metro",
    "company-name",
    "company-description",
    "logo",
    "site",
    "email",
    "phone",
    "contact-name",
    "hr-agency"
]

FILE_NAME = "OBV_full.xml"


EMAIL_REGEX = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)
PHONE_REGEX = re.compile("^([+\d\(\)\-\ ])*$", re.IGNORECASE) 


# Функция для вытягивания текста из узлов XML с последующей заменой в тексте `,` на `;` (Для CSV)
def extract_text(node, tag_name):
    tag = node.find(tag_name)
    if tag is not None:
        text = tag.text
        if text is not None:
            return text.replace(',', ';')
    return None

# Функция для удаления HTML тегов, e.g. <p>, <h1>, etc
def remove_html_tags(raw_html):
  cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

#Парсим
xml = ET.parse(FILE_NAME)
root = xml.getroot()

result_list = []

#Итерация по каждой вакансии
for node in root.iter(VACANCY_TAG):
    #Достаем все текстовые теги
    url = extract_text(node, URL_TAG)
    mobile_url = extract_text(node, MOBILE_URL_TAG)
    creation_date = extract_text(node, CREATION_DATE_TAG)
    update_date = extract_text(node, UPDATE_DATE_TAG)
    
    salary = extract_text(node, SALARY_TAG)
    
    min_salary = None
    max_salary = None
    
    #Парсим зарплату. Два формата: от XXXX до XXXX, либо от/до XXXX.
    if salary:
        parts = salary.lower().split()
        if len(parts) == 4:
            min_salary = int(parts[1])
            max_salary = int(parts[3])
        elif len(salary) == 2:
            if salary[0] == 'от':
                min_salary = int(parts[1])
            else:
                max_salary = int(parts[1])
    
    currency = extract_text(node, CURRENCY_TAG)
    
    category = node.find(CATEGORY_TAG)
    industry = None
    if category and len(category):
        industry = extract_text(category, INDUSTRY_TAG)
    
    job_name = extract_text(node, JOB_NAME_TAG)
    employment = extract_text(node, EMPLOYMENT_TAG)
    schedule = extract_text(node, SCHEDULE_TAG)
    
    description = extract_text(node, DESCRIPTION_TAG)
    if description:
        description = remove_html_tags(description)
        
    duty = extract_text(node, DUTY_TAG)
    if duty:
        duty = remove_html_tags(duty)
    
    term = node.find(TERM_TAG)
    text = None
    if term and len(term):
        text = extract_text(term, TEXT_TAG)
        if text:
            text = remove_html_tags(text)
    
    requirement = node.find(REQUIREMENT_TAG)
    education = None
    qualification = None
    experience = None
    
    if requirement and len(requirement):
        education = extract_text(requirement, EDUCATION_TAG)
        qualification = extract_text(requirement, QUALIFICATION_TAG)
        if qualification:
            qualification = remove_html_tags(qualification)
        experience = extract_text(requirement, EXPERIENCE_TAG)
    
    addresses = node.find(ADDRESSES_TAG)
    
    location = None
    longitude = None
    latitude = None
    metro = None
    
    #Внутри тега addresses во всем XML находится только 1 тег address
    if addresses and len(addresses):
        address = addresses.find(ADDRESS_TAG)
        if address and len(address):
            location = extract_text(address, LOCATION_TAG)
            longitude = extract_text(address, LONGTITUDE_TAG)
            latitude = extract_text(address, LATITUDE_TAG)
            #Может быть несколько тегов metro
            metro = ";".join([metro.text for metro in address.iter(METRO_TAG)])
    
    company = node.find(COMPANY_TAG)
    
    company_name = None
    company_description = None
    logo = None
    site = None
    email = None
    phone = None
    contact_name = None
    hr_agency = None
    
    if company and len(company):
        company_name = extract_text(company, NAME_TAG)
        company_description = extract_text(company, DESCRIPTION_TAG)
        if company_description:
            company_description = remove_html_tags(company_description)
        logo = extract_text(company, LOGO_TAG)
        site = extract_text(company, SITE_TAG)
        
        phones = []
        
        phone_candidate = extract_text(company, PHONE_TAG)
        if phone_candidate:
            phones.append(phone_candidate)
        
        #Может быть несколько тегов email
        raw_emails = [email.text for email in company.iter(EMAIL_TAG)]
        emails = []
        
        #В некоторых случаях в теге email может находится номер телефона, который тоже необходимо добавить в "телефоны"
        #Определяем тип регуляркой
        for string in raw_emails:
            if EMAIL_REGEX.match(string):
                emails.append(string)
            elif PHONE_REGEX.match(string):
                phones.append(string)
        
        phone = ";".join(phones)
        email = ";".join(emails)
        
        contact_name = extract_text(company, CONTACT_NAME_TAG)
        hr_agency = extract_text(company, HR_AGENCY_TAG)

    result_list.append([
            url, mobile_url, creation_date, update_date, min_salary, max_salary,
            currency, industry, job_name, employment, schedule, description, duty, text,
            education, qualification, experience, location, longitude, latitude, metro,
            company_name, company_description, logo, site, email, phone, contact_name, hr_agency])




df = pd.DataFrame(result_list, columns=CSV_COLUMNS)
df[:10000].to_csv("data_frame_part.csv", encoding='utf-8')
#df.to_csv("data_frame.csv", encoding='utf-8')
