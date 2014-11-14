#{"url":, "event":, "product_id":, "site_id":, "server_name":,}

rows = [
    {"product_id" : 0, "event" : 0, "url" : "http://www.tesco.com/direct/zoggs-miss-zoggy-swimfree-float-suit/114-5843.prd", "site_id" : "tesco", "server_name": "test_process"},
    {"product_id" : 0, "event" : 0, "url" : "http://www.tesco.com/direct/intel-4th-generation-core-i5-4670-34ghz-quad-core-processor-6mb-l3-cache-boxed/518-7080.prd", "site_id" : "tesco", "server_name": "test_process"},
    {"product_id" : 0, "event" : 0, "url" : "http://www.tesco.com/direct/3-piece-titanium-step-drill-set/793-7483.prd", "site_id" : "tesco", "server_name": "test_process"},
    {"product_id" : 0, "event" : 0, "url" : "http://www.tesco.com/direct/intel-4th-generation-core-i5-4670-34ghz-quad-core-processor-6mb-l3-cache-boxed/518-7080.prd", "site_id" : "tesco", "server_name": "test_process"},
    {"product_id" : 0, "event" : 0, "url" : "http://www.tesco.com/direct/silverline-hammer-drill-1010w/212-2308.prd?skuId=212-2308", "site_id" : "tesco", "server_name": "test_process"},
]
    
 

class CrawlerList():
    def __init__(self):
        pass
    def get_rows(self):
        return rows

if __name__ == "__main__":
    print(get_urls())
