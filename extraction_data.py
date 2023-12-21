import re

def extract_text_with_markers(text, start_marker, end_markers=None):
    results = []
    
    if end_markers is None:
        pattern = re.escape(start_marker) + r"(.*?)$"
        result = re.findall(pattern, text)
        if result:
            results.extend(result)
    else:
        for end_marker in end_markers:
            pattern = re.escape(start_marker) + r"(.*?)" + re.escape(end_marker)
            result = re.findall(pattern, text)
            if result:
                results.extend(result)
    
    return results

def retry_extraction_with_different_markers(text, start_markers, end_markers, printer=False):
    for start_marker in start_markers:
        results = extract_text_with_markers(text, start_marker, end_markers)
        if results:
            if printer:
                print(len(results), results)
            results = [result for result in results if result != ""]
            
            return min(results, key=len)
    return "-"

def text_extranc(data, start_markers, end_markers, printer=False):
    data = [text for text in data if (text != None)]
    data_E = list()
    for i in data:
        text = ""
        if type(i) is str:
            text = i
            data_E.append(text)
        elif type(i) is dict:
            for j,n in i.items():
                if type(n) is dict:
                    text = n['#text']
                    data_E.append(text)
                elif (type(n) is str) & (j == "#text"):
                    text = n
                    data_E.append(text)
                elif type(n) is list:
                    for k in n:
                        if (type(k) is dict):
                            if (len(k) != 1):
                                text = k['#text']
                                data_E.append(text)
                        elif type(k) is str:
                            text = k
                            data_E.append(text)
        elif len(i) == 1:
            pass
        else:
            text = i['#text']
            data_E.append(text)
    
    i = 0
    while i < len(data_E):
        if "\n" in data_E[i]:
            data_E[i] = data_E[i].replace("\n", " "+data_E[i-1])
            del data_E[i-1]
        else:
            i += 1

    
    data = " ".join(data_E)
    data = retry_extraction_with_different_markers(data, start_markers, end_markers, printer=printer).strip()
    return data

def remove_hex_color_codes(text):
    pattern = r"0X[\dA-Fa-f]+"
    result = re.sub(pattern, "", text)
    return result


def preprocessing_date(date):
    if date == "-":
        return date
    # "-"를 기준으로 날짜를 분할
    year, month, day = date.split("-")

    # 월과 일이 한 자리 수인 경우 앞에 0을 붙여 두 자리로 만듦
    month = month.zfill(2)
    day = day.zfill(2)

    # 결과 출력
    formatted_date = f"{year}-{month}-{day}"
    return formatted_date