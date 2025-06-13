# Hướng Dẫn Cập Nhật Dữ Liệu Phụ Gia Thực Phẩm

## 1. Giới Thiệu

Tài liệu này cung cấp hướng dẫn chi tiết về cách cập nhật và duy trì danh mục phụ gia thực phẩm theo mức độ rủi ro. Việc cập nhật thường xuyên là rất quan trọng vì các đánh giá khoa học và quy định về phụ gia thường xuyên thay đổi dựa trên nghiên cứu mới.

Có hai phương pháp chính để cập nhật dữ liệu:
1. **Cập nhật thủ công**: Phù hợp cho các cập nhật nhỏ hoặc khi cần kiểm soát chặt chẽ nội dung
2. **Cập nhật tự động**: Phù hợp cho việc đồng bộ hóa với các cơ sở dữ liệu lớn

## 2. Cập Nhật Thủ Công

### 2.1. Theo Dõi Nguồn Chính Thức

#### EFSA (Cơ quan An toàn Thực phẩm Châu Âu)
- **Website**: https://www.efsa.europa.eu/en/topics/topic/food-additives
- **Tần suất kiểm tra**: Hàng tháng
- **Cách thức**:
  - Truy cập mục "Scientific Opinions" và lọc theo "Food Additives"
  - Tìm các đánh giá mới nhất về phụ gia (re-evaluation)
  - Cập nhật thông tin vào danh mục, đặc biệt là các thay đổi về ADI (Acceptable Daily Intake) hoặc mức độ rủi ro

#### FDA (Cục Quản lý Thực phẩm và Dược phẩm Hoa Kỳ)
- **Website**: https://www.fda.gov/food/food-additives-petitions/food-additive-status-list
- **Tần suất kiểm tra**: Hàng quý
- **Cách thức**:
  - Kiểm tra danh sách "Food Additive Status List" để cập nhật trạng thái phê duyệt
  - Theo dõi mục "Food Ingredients and Packaging" để biết các thông báo mới

#### IARC (Cơ quan Nghiên cứu Ung thư Quốc tế)
- **Website**: https://monographs.iarc.who.int/
- **Tần suất kiểm tra**: Hàng quý
- **Cách thức**:
  - Kiểm tra các monograph mới về đánh giá khả năng gây ung thư của các chất
  - Cập nhật phân loại rủi ro nếu có thay đổi (đặc biệt là các phụ gia được đưa vào nhóm 1, 2A, 2B)

### 2.2. Cập Nhật Từ Tệp CSV/Excel

Nhiều cơ quan quản lý cung cấp dữ liệu dưới dạng tệp CSV hoặc Excel. Dưới đây là quy trình cập nhật từ các tệp này:

1. **Tải xuống tệp dữ liệu mới nhất**:
   - FSA UK: https://www.food.gov.uk/business-guidance/approved-additives-and-e-numbers (tải xuống từ trang này)
   - EU Food Additives Database: https://food.ec.europa.eu/safety/food-improvement-agents/additives/database_en

2. **Chuẩn hóa định dạng**:
   ```
   # Mẫu cấu trúc CSV chuẩn
   E-number,Tên tiếng Anh,Tên tiếng Việt,Mức độ rủi ro,Nguồn đánh giá,Ngày cập nhật,Ghi chú
   E100,Curcumin,Nghệ,Xanh Lá,EFSA 2020,2023-06-01,Chiết xuất tự nhiên
   ```

3. **So sánh và hợp nhất dữ liệu**:
   - Sử dụng Excel hoặc Google Sheets với công thức VLOOKUP/HLOOKUP để so sánh dữ liệu mới với dữ liệu hiện có
   - Đánh dấu các mục có sự khác biệt để xem xét kỹ hơn
   - Ưu tiên nguồn mới nhất khi có mâu thuẫn

4. **Lưu trữ phiên bản**:
   - Đặt tên tệp theo định dạng: `additives_database_YYYY-MM-DD.csv`
   - Lưu trữ các phiên bản cũ để tham khảo và kiểm tra lịch sử thay đổi

### 2.3. Cập Nhật Từ Nghiên Cứu Khoa Học

1. **Thiết lập Google Scholar Alerts**:
   - Tạo cảnh báo với từ khóa như "food additives safety", "E-number toxicity", "food colorings health"
   - Xem xét các nghiên cứu mới từ các tạp chí uy tín (Food and Chemical Toxicology, Food Additives & Contaminants, ...)

2. **Đánh giá nghiên cứu**:
   - Kiểm tra phương pháp nghiên cứu và cỡ mẫu
   - Xác định liệu nghiên cứu có được bình duyệt không
   - Đánh giá mức độ đồng thuận với các nghiên cứu khác

3. **Cập nhật có chọn lọc**:
   - Chỉ cập nhật dựa trên nghiên cứu có chất lượng cao
   - Ghi chú rõ nguồn và ngày nghiên cứu
   - Đánh dấu mức độ tin cậy của thông tin (ví dụ: "Đã xác nhận", "Cần thêm nghiên cứu")

## 3. Cập Nhật Tự Động

### 3.1. Sử Dụng API của Open Food Facts

Open Food Facts cung cấp API và tệp JSON đầy đủ về phụ gia thực phẩm, rất hữu ích cho việc cập nhật tự động.

#### Tải Tệp JSON Đầy Đủ

```python
import requests
import json
import pandas as pd
from datetime import datetime

# Tải tệp JSON từ Open Food Facts
def download_additives_json():
    url = "https://static.openfoodfacts.org/data/taxonomies/additives.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        # Lưu tệp JSON gốc để tham khảo
        with open(f"additives_raw_{datetime.now().strftime('%Y%m%d')}.json", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        # Chuyển đổi thành đối tượng Python
        return json.loads(response.text)
    else:
        print(f"Lỗi khi tải tệp: {response.status_code}")
        return None

# Xử lý dữ liệu từ JSON thành DataFrame
def process_additives_data(data):
    additives_list = []
    
    for key, value in data.items():
        if key.startswith("en:e"):
            additive = {}
            
            # Lấy mã E-number
            e_number = value.get("e_number", {}).get("en", "")
            
            # Lấy tên tiếng Anh
            name_en = value.get("name", {}).get("en", "")
            
            # Lấy tên tiếng Việt nếu có
            name_vi = value.get("name", {}).get("vi", "")
            
            # Kiểm tra trạng thái vegetarian/vegan
            vegetarian = value.get("vegetarian", {}).get("en", "")
            vegan = value.get("vegan", {}).get("en", "")
            
            # Lấy thông tin đánh giá EFSA nếu có
            efsa_evaluation = value.get("efsa_evaluation", {}).get("en", "")
            efsa_url = value.get("efsa_evaluation_url", {}).get("en", "")
            efsa_date = value.get("efsa_evaluation_date", {}).get("en", "")
            
            # Lấy thông tin phân loại
            additives_classes = value.get("additives_classes", {}).get("en", "")
            
            # Thêm vào danh sách
            additive = {
                "e_number": e_number,
                "key": key,
                "name_en": name_en,
                "name_vi": name_vi,
                "vegetarian": vegetarian,
                "vegan": vegan,
                "efsa_evaluation": efsa_evaluation,
                "efsa_url": efsa_url,
                "efsa_date": efsa_date,
                "additives_classes": additives_classes
            }
            
            additives_list.append(additive)
    
    # Chuyển đổi thành DataFrame
    df = pd.DataFrame(additives_list)
    
    # Lưu thành CSV
    df.to_csv(f"additives_processed_{datetime.now().strftime('%Y%m%d')}.csv", index=False, encoding="utf-8")
    
    return df

# Thực thi
additives_data = download_additives_json()
if additives_data:
    additives_df = process_additives_data(additives_data)
    print(f"Đã xử lý {len(additives_df)} phụ gia.")
```

#### Tích Hợp Với Cơ Sở Dữ Liệu Hiện Có

```python
import pandas as pd
from datetime import datetime

# Đọc cơ sở dữ liệu hiện có
def merge_with_existing_database():
    # Đọc tệp CSV mới đã xử lý
    new_data = pd.read_csv(f"additives_processed_{datetime.now().strftime('%Y%m%d')}.csv")
    
    try:
        # Đọc cơ sở dữ liệu hiện có
        existing_data = pd.read_csv("additives_database.csv")
        
        # Hợp nhất dữ liệu, ưu tiên thông tin mới
        merged = existing_data.copy()
        
        # Đếm số lượng cập nhật
        updates = 0
        new_entries = 0
        
        # Duyệt qua dữ liệu mới
        for index, row in new_data.iterrows():
            e_number = row['e_number']
            
            # Kiểm tra xem phụ gia đã tồn tại chưa
            if e_number in existing_data['e_number'].values:
                # Cập nhật thông tin mới
                mask = existing_data['e_number'] == e_number
                
                # Chỉ cập nhật các trường có giá trị
                for col in new_data.columns:
                    if pd.notna(row[col]) and row[col] != "":
                        merged.loc[mask, col] = row[col]
                
                updates += 1
            else:
                # Thêm phụ gia mới
                merged = pd.concat([merged, pd.DataFrame([row])], ignore_index=True)
                new_entries += 1
        
        # Lưu cơ sở dữ liệu đã cập nhật
        merged.to_csv("additives_database.csv", index=False, encoding="utf-8")
        
        # Tạo bản sao lưu
        merged.to_csv(f"additives_database_backup_{datetime.now().strftime('%Y%m%d')}.csv", index=False, encoding="utf-8")
        
        print(f"Đã cập nhật {updates} phụ gia và thêm {new_entries} phụ gia mới.")
        return merged
        
    except FileNotFoundError:
        # Nếu chưa có cơ sở dữ liệu, sử dụng dữ liệu mới
        new_data.to_csv("additives_database.csv", index=False, encoding="utf-8")
        print(f"Đã tạo cơ sở dữ liệu mới với {len(new_data)} phụ gia.")
        return new_data

# Thực thi
updated_database = merge_with_existing_database()
```

### 3.2. Crawl Dữ Liệu Từ Wikipedia

Wikipedia cung cấp danh sách E-number khá đầy đủ. Dưới đây là script để crawl dữ liệu này:

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def crawl_wikipedia_e_numbers():
    # URL của trang Wikipedia về E-numbers
    url = "https://en.wikipedia.org/wiki/E_number"
    
    # Tải trang
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm tất cả các bảng trong trang
        tables = soup.find_all('table', {'class': 'wikitable'})
        
        all_additives = []
        
        # Duyệt qua từng bảng
        for table in tables:
            # Kiểm tra xem bảng có phải là bảng E-number không
            headers = table.find_all('th')
            header_texts = [header.get_text(strip=True) for header in headers]
            
            # Kiểm tra các tiêu đề phổ biến trong bảng E-number
            if any(keyword in ' '.join(header_texts).lower() for keyword in ['code', 'name', 'status']):
                rows = table.find_all('tr')
                
                # Bỏ qua hàng tiêu đề
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        # Trích xuất thông tin
                        e_code = cells[0].get_text(strip=True)
                        name = cells[1].get_text(strip=True)
                        
                        # Trích xuất trạng thái nếu có
                        status = ""
                        if len(cells) >= 3:
                            status = cells[2].get_text(strip=True)
                        
                        # Thêm vào danh sách
                        if e_code and e_code.startswith('E'):
                            all_additives.append({
                                'e_number': e_code,
                                'name_en': name,
                                'status': status,
                                'source': 'Wikipedia',
                                'date_crawled': datetime.now().strftime('%Y-%m-%d')
                            })
        
        # Chuyển đổi thành DataFrame
        df = pd.DataFrame(all_additives)
        
        # Lưu thành CSV
        df.to_csv(f"wikipedia_additives_{datetime.now().strftime('%Y%m%d')}.csv", index=False, encoding="utf-8")
        
        print(f"Đã crawl {len(df)} phụ gia từ Wikipedia.")
        return df
    else:
        print(f"Lỗi khi tải trang: {response.status_code}")
        return None

# Thực thi
wikipedia_additives = crawl_wikipedia_e_numbers()
```

### 3.3. Crawl Dữ Liệu Từ FSA UK

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def crawl_fsa_additives():
    # URL của trang FSA UK về phụ gia
    url = "https://www.food.gov.uk/business-guidance/approved-additives-and-e-numbers"
    
    # Tải trang
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm các phần về phụ gia
        sections = soup.find_all(['h2', 'h3'])
        
        all_additives = []
        current_category = ""
        
        # Duyệt qua từng phần
        for section in sections:
            # Lấy tiêu đề phần
            section_title = section.get_text(strip=True)
            
            # Kiểm tra xem đây có phải là phần về phụ gia không
            if any(keyword in section_title.lower() for keyword in ['colours', 'preservatives', 'antioxidants', 'sweeteners', 'emulsifiers', 'stabilisers']):
                current_category = section_title
                
                # Tìm danh sách phụ gia trong phần này
                next_element = section.find_next(['ul', 'ol', 'table'])
                
                if next_element:
                    # Nếu là bảng
                    if next_element.name == 'table':
                        rows = next_element.find_all('tr')
                        for row in rows[1:]:  # Bỏ qua hàng tiêu đề
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 2:
                                e_code = cells[0].get_text(strip=True)
                                name = cells[1].get_text(strip=True)
                                
                                if e_code and e_code.startswith('E'):
                                    all_additives.append({
                                        'e_number': e_code,
                                        'name_en': name,
                                        'category': current_category,
                                        'source': 'FSA UK',
                                        'date_crawled': datetime.now().strftime('%Y-%m-%d')
                                    })
                    
                    # Nếu là danh sách
                    elif next_element.name in ['ul', 'ol']:
                        items = next_element.find_all('li')
                        for item in items:
                            text = item.get_text(strip=True)
                            # Tìm mã E-number trong văn bản
                            if 'E' in text:
                                parts = text.split(' - ', 1)
                                if len(parts) >= 2:
                                    e_code = parts[0].strip()
                                    name = parts[1].strip()
                                    
                                    if e_code and e_code.startswith('E'):
                                        all_additives.append({
                                            'e_number': e_code,
                                            'name_en': name,
                                            'category': current_category,
                                            'source': 'FSA UK',
                                            'date_crawled': datetime.now().strftime('%Y-%m-%d')
                                        })
        
        # Chuyển đổi thành DataFrame
        df = pd.DataFrame(all_additives)
        
        # Lưu thành CSV
        df.to_csv(f"fsa_additives_{datetime.now().strftime('%Y%m%d')}.csv", index=False, encoding="utf-8")
        
        print(f"Đã crawl {len(df)} phụ gia từ FSA UK.")
        return df
    else:
        print(f"Lỗi khi tải trang: {response.status_code}")
        return None

# Thực thi
fsa_additives = crawl_fsa_additives()
```

### 3.4. Tự Động Hóa Quy Trình Cập Nhật

Để tự động hóa toàn bộ quy trình, bạn có thể tạo một script chính kết hợp tất cả các bước trên:

```python
import schedule
import time
from datetime import datetime
import logging

# Thiết lập logging
logging.basicConfig(
    filename=f"additives_update_log_{datetime.now().strftime('%Y%m%d')}.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def update_additives_database():
    logging.info("Bắt đầu cập nhật cơ sở dữ liệu phụ gia...")
    
    try:
        # 1. Tải và xử lý dữ liệu từ Open Food Facts
        logging.info("Đang tải dữ liệu từ Open Food Facts...")
        additives_data = download_additives_json()
        if additives_data:
            additives_df = process_additives_data(additives_data)
            logging.info(f"Đã xử lý {len(additives_df)} phụ gia từ Open Food Facts.")
        
        # 2. Crawl dữ liệu từ Wikipedia
        logging.info("Đang crawl dữ liệu từ Wikipedia...")
        wikipedia_additives = crawl_wikipedia_e_numbers()
        
        # 3. Crawl dữ liệu từ FSA UK
        logging.info("Đang crawl dữ liệu từ FSA UK...")
        fsa_additives = crawl_fsa_additives()
        
        # 4. Hợp nhất dữ liệu
        logging.info("Đang hợp nhất dữ liệu...")
        updated_database = merge_with_existing_database()
        
        # 5. Tạo báo cáo cập nhật
        logging.info("Đang tạo báo cáo cập nhật...")
        create_update_report()
        
        logging.info("Cập nhật cơ sở dữ liệu phụ gia hoàn tất.")
        
    except Exception as e:
        logging.error(f"Lỗi trong quá trình cập nhật: {str(e)}")

def create_update_report():
    # Tạo báo cáo về các thay đổi
    report = f"""
    BÁO CÁO CẬP NHẬT CƠ SỞ DỮ LIỆU PHỤ GIA
    Ngày: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    1. Tổng số phụ gia trong cơ sở dữ liệu: {len(pd.read_csv("additives_database.csv"))}
    2. Số phụ gia được cập nhật: {updates}
    3. Số phụ gia mới được thêm: {new_entries}
    4. Nguồn dữ liệu:
       - Open Food Facts: {len(additives_df) if 'additives_df' in locals() else 0} phụ gia
       - Wikipedia: {len(wikipedia_additives) if 'wikipedia_additives' in locals() else 0} phụ gia
       - FSA UK: {len(fsa_additives) if 'fsa_additives' in locals() else 0} phụ gia
    
    Các phụ gia có thay đổi đáng chú ý:
    [Danh sách các phụ gia có thay đổi quan trọng]
    """
    
    with open(f"update_report_{datetime.now().strftime('%Y%m%d')}.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    logging.info("Đã tạo báo cáo cập nhật.")

# Lên lịch cập nhật hàng tuần
schedule.every().monday.at("03:00").do(update_additives_database)

# Chạy lần đầu
update_additives_database()

# Vòng lặp chính
while True:
    schedule.run_pending()
    time.sleep(3600)  # Kiểm tra mỗi giờ
```

## 4. Cập Nhật Mức Độ Rủi Ro

Việc cập nhật mức độ rủi ro là phần quan trọng nhất và cần được thực hiện cẩn thận:

### 4.1. Quy Tắc Phân Loại Rủi Ro

Để đảm bảo tính nhất quán, hãy tuân theo các quy tắc sau khi phân loại mức độ rủi ro:

1. **Không Rủi Ro (Xanh Lá)**:
   - Phụ gia có đánh giá "an toàn" từ ít nhất 2 cơ quan quản lý (EFSA, FDA, JECFA)
   - Không có nghiên cứu mới chỉ ra mối lo ngại
   - Thường là các chất tự nhiên hoặc vitamin thiết yếu

2. **Rủi Ro Hạn Chế (Vàng)**:
   - Phụ gia được coi là an toàn nhưng có một số báo cáo về phản ứng nhẹ
   - Có ADI (Acceptable Daily Intake) thấp
   - Có thể gây kích ứng nhẹ ở một số người nhạy cảm

3. **Rủi Ro Vừa Phải (Cam)**:
   - Phụ gia có báo cáo về phản ứng dị ứng đáng kể
   - Có nghiên cứu chỉ ra tác động tiêu cực tiềm ẩn
   - Bị hạn chế sử dụng ở một số quốc gia

4. **Rủi Ro Cao (Đỏ)**:
   - Phụ gia bị cấm ở ít nhất một quốc gia phát triển
   - Được IARC phân loại vào nhóm 1, 2A hoặc 2B (gây ung thư)
   - Có nghiên cứu mạnh mẽ chỉ ra tác động tiêu cực nghiêm trọng

### 4.2. Quy Trình Cập Nhật Mức Độ Rủi Ro

```python
def update_risk_levels():
    # Đọc cơ sở dữ liệu hiện có
    df = pd.read_csv("additives_database.csv")
    
    # Đọc các quy tắc phân loại rủi ro
    risk_rules = pd.read_csv("risk_classification_rules.csv")
    
    # Duyệt qua từng phụ gia
    for index, row in df.iterrows():
        e_number = row['e_number']
        
        # Kiểm tra các điều kiện rủi ro cao (Đỏ)
        if (row['banned_countries'] > 0 or 
            'group 1' in str(row['iarc_classification']).lower() or 
            'group 2a' in str(row['iarc_classification']).lower() or 
            'group 2b' in str(row['iarc_classification']).lower() or
            'high concern' in str(row['efsa_evaluation']).lower()):
            df.at[index, 'risk_level'] = 'Đỏ'
            continue
        
        # Kiểm tra các điều kiện rủi ro vừa phải (Cam)
        if (row['allergy_reports'] > 5 or 
            'restricted' in str(row['usage_status']).lower() or
            'moderate concern' in str(row['efsa_evaluation']).lower()):
            df.at[index, 'risk_level'] = 'Cam'
            continue
        
        # Kiểm tra các điều kiện rủi ro hạn chế (Vàng)
        if (row['allergy_reports'] > 0 or 
            row['adi_value'] < 10 or
            'minor concern' in str(row['efsa_evaluation']).lower()):
            df.at[index, 'risk_level'] = 'Vàng'
            continue
        
        # Mặc định là không rủi ro (Xanh Lá)
        df.at[index, 'risk_level'] = 'Xanh Lá'
    
    # Lưu cơ sở dữ liệu đã cập nhật
    df.to_csv("additives_database.csv", index=False, encoding="utf-8")
    
    print(f"Đã cập nhật mức độ rủi ro cho {len(df)} phụ gia.")
```

### 4.3. Đối Chiếu Với Yuka

Để đảm bảo tính nhất quán với hệ thống đánh giá của Yuka, bạn có thể thực hiện đối chiếu:

```python
def compare_with_yuka():
    # Đọc cơ sở dữ liệu hiện có
    df = pd.read_csv("additives_database.csv")
    
    # Đọc dữ liệu từ Yuka (nếu có)
    try:
        yuka_data = pd.read_csv("yuka_additives.csv")
        
        # Duyệt qua từng phụ gia
        for index, row in df.iterrows():
            e_number = row['e_number']
            
            # Tìm phụ gia tương ứng trong dữ liệu Yuka
            yuka_match = yuka_data[yuka_data['e_number'] == e_number]
            
            if not yuka_match.empty:
                yuka_risk = yuka_match.iloc[0]['risk_level']
                current_risk = row['risk_level']
                
                # Ghi chú nếu có sự khác biệt
                if yuka_risk != current_risk:
                    df.at[index, 'notes'] = f"{row['notes']} | Khác biệt với Yuka: Yuka={yuka_risk}, Hiện tại={current_risk}"
                    df.at[index, 'needs_review'] = True
        
        # Lưu cơ sở dữ liệu đã cập nhật
        df.to_csv("additives_database.csv", index=False, encoding="utf-8")
        
        print(f"Đã đối chiếu với dữ liệu Yuka.")
    except FileNotFoundError:
        print("Không tìm thấy dữ liệu Yuka để đối chiếu.")
```

## 5. Xuất Dữ Liệu Cho Ứng Dụng

### 5.1. Xuất Dữ Liệu Dạng JSON

```python
def export_to_json():
    # Đọc cơ sở dữ liệu
    df = pd.read_csv("additives_database.csv")
    
    # Chuyển đổi thành định dạng JSON phù hợp cho ứng dụng
    additives_json = {}
    
    for index, row in df.iterrows():
        e_number = row['e_number']
        
        # Xác định mã màu dựa trên mức độ rủi ro
        risk_color = "green"
        if row['risk_level'] == 'Vàng':
            risk_color = "yellow"
        elif row['risk_level'] == 'Cam':
            risk_color = "orange"
        elif row['risk_level'] == 'Đỏ':
            risk_color = "red"
        
        # Tạo đối tượng JSON cho phụ gia
        additives_json[e_number] = {
            "name": {
                "en": row['name_en'],
                "vi": row['name_vi'] if pd.notna(row['name_vi']) else row['name_en']
            },
            "risk_level": row['risk_level'],
            "risk_color": risk_color,
            "category": row['category'] if pd.notna(row['category']) else "",
            "description": {
                "en": row['description_en'] if pd.notna(row['description_en']) else "",
                "vi": row['description_vi'] if pd.notna(row['description_vi']) else ""
            },
            "sources": row['sources'] if pd.notna(row['sources']) else "",
            "last_updated": datetime.now().strftime('%Y-%m-%d')
        }
    
    # Lưu thành tệp JSON
    with open("additives_app_data.json", "w", encoding="utf-8") as f:
        json.dump(additives_json, f, ensure_ascii=False, indent=2)
    
    print(f"Đã xuất dữ liệu cho ứng dụng thành công.")
```

### 5.2. Xuất Dữ Liệu Dạng SQLite

```python
import sqlite3

def export_to_sqlite():
    # Đọc cơ sở dữ liệu
    df = pd.read_csv("additives_database.csv")
    
    # Kết nối đến cơ sở dữ liệu SQLite
    conn = sqlite3.connect("additives.db")
    
    # Tạo bảng
    conn.execute('''
    CREATE TABLE IF NOT EXISTS additives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        e_number TEXT UNIQUE,
        name_en TEXT,
        name_vi TEXT,
        risk_level TEXT,
        risk_color TEXT,
        category TEXT,
        description_en TEXT,
        description_vi TEXT,
        sources TEXT,
        last_updated TEXT
    )
    ''')
    
    # Xóa dữ liệu cũ
    conn.execute("DELETE FROM additives")
    
    # Thêm dữ liệu mới
    for index, row in df.iterrows():
        e_number = row['e_number']
        
        # Xác định mã màu dựa trên mức độ rủi ro
        risk_color = "green"
        if row['risk_level'] == 'Vàng':
            risk_color = "yellow"
        elif row['risk_level'] == 'Cam':
            risk_color = "orange"
        elif row['risk_level'] == 'Đỏ':
            risk_color = "red"
        
        # Thêm vào cơ sở dữ liệu
        conn.execute('''
        INSERT INTO additives (
            e_number, name_en, name_vi, risk_level, risk_color, 
            category, description_en, description_vi, sources, last_updated
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            e_number,
            row['name_en'],
            row['name_vi'] if pd.notna(row['name_vi']) else row['name_en'],
            row['risk_level'],
            risk_color,
            row['category'] if pd.notna(row['category']) else "",
            row['description_en'] if pd.notna(row['description_en']) else "",
            row['description_vi'] if pd.notna(row['description_vi']) else "",
            row['sources'] if pd.notna(row['sources']) else "",
            datetime.now().strftime('%Y-%m-%d')
        ))
    
    # Lưu thay đổi
    conn.commit()
    
    # Đóng kết nối
    conn.close()
    
    print(f"Đã xuất dữ liệu sang SQLite thành công.")
```

## 6. Lưu Ý Quan Trọng

1. **Tần Suất Cập Nhật**:
   - Cập nhật thủ công: Ít nhất 3 tháng/lần
   - Cập nhật tự động: Hàng tuần hoặc hàng tháng

2. **Xử Lý Mâu Thuẫn**:
   - Khi có mâu thuẫn giữa các nguồn, ưu tiên theo thứ tự: EFSA > FDA > JECFA > Các nguồn khác
   - Ưu tiên đánh giá mới nhất
   - Áp dụng nguyên tắc phòng ngừa: nếu có nghi ngờ, chọn mức độ rủi ro cao hơn

3. **Bảo Mật Dữ Liệu**:
   - Luôn tạo bản sao lưu trước khi cập nhật
   - Lưu trữ lịch sử thay đổi để có thể khôi phục nếu cần

4. **Tài Liệu Hóa**:
   - Ghi chú rõ nguồn và ngày cập nhật cho mỗi thay đổi
   - Tạo báo cáo cập nhật sau mỗi lần cập nhật lớn

## 7. Tài Nguyên Bổ Sung

### 7.1. API và Nguồn Dữ Liệu

1. **Open Food Facts API**:
   - URL: https://world.openfoodfacts.org/data
   - Tài liệu: https://openfoodfacts.github.io/openfoodfacts-server/api/

2. **EFSA OpenFoodTox**:
   - URL: https://www.efsa.europa.eu/en/data-report/chemical-hazards-database-openfoodtox

3. **FDA Food Additive Status List**:
   - URL: https://www.fda.gov/food/food-additives-petitions/food-additive-status-list

4. **Codex Alimentarius**:
   - URL: http://www.fao.org/fao-who-codexalimentarius/codex-texts/dbs/gsfa/en/

### 7.2. Thư Viện Python Hữu Ích

1. **Pandas**: Xử lý dữ liệu dạng bảng
2. **Requests**: Tải dữ liệu từ web
3. **BeautifulSoup**: Phân tích HTML
4. **Schedule**: Lên lịch tự động hóa
5. **SQLite3**: Lưu trữ cơ sở dữ liệu nhẹ

## 8. Kết Luận

Việc duy trì một danh mục phụ gia thực phẩm cập nhật và chính xác là một quá trình liên tục. Bằng cách kết hợp cập nhật thủ công và tự động, bạn có thể đảm bảo rằng dữ liệu luôn phản ánh các đánh giá khoa học mới nhất và quy định hiện hành.

Hãy nhớ rằng mục tiêu cuối cùng là cung cấp thông tin chính xác và hữu ích cho người dùng, giúp họ đưa ra quyết định sáng suốt về thực phẩm họ tiêu thụ.
