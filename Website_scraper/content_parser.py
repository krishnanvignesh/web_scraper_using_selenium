class ContentParser:
    def __init__(self, soup, pest):
        self._soup = soup
        self.pest = pest
        self.product_data = {'pest': pest}

    def extract(self):
        self.__extract_origin()
        self.__extract_description()

    def __extract_origin(self):
        pest_info = []
        div = self._soup.find_all('div', {"class": "pest-header-content"})
        if div:
            para = div[0].find_all('p')
            for p_tag in para:
                pest_info.append(p_tag.text)
            pest_info = ''.join(pest_info).replace('\n', ',')
        self.product_data['origin'] = pest_info

    def __extract_description(self):
        div_desc = self._soup.find_all('div', {"class": "collapsefaq-content"})
        if div_desc:
            self.product_data['See if you can identify the pest'] = div_desc[0].text
            self.product_data['Check what can legally come into Australia'] = div_desc[1].text
            self.product_data['Secure any suspect specimens'] = div_desc[2].text

    @staticmethod
    def __clean_attribute(attribute):
        attribute = attribute.replace(':', '')
        attribute = attribute.strip()
        return attribute

    def get_product_data(self):
        return self.product_data
