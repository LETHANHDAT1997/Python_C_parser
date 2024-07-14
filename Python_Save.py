import re
# from pycparser import c_parser, c_ast

# Mã nguồn C cần phân tích
c_code = """
/* A simple example that demonstrates how to create GET and POST
 * handlers for the web server.
 */
extern const uint8_t index_html_start[] asm("_binary_webserver_html_start");
extern const uint8_t index_html_end[] asm("_binary_webserver_html_end");

static const char *TAG = "example";
static httpd_handle_t server = NULL;

static switch_handle_t p_switch_handle = NULL;
static slider_handle_t p_slider_handle = NULL;
static rgb_handler_t p_rgb_handle = NULL;

/* An HTTP GET handler */
static esp_err_t http_get_handler(httpd_req_t *req)
{
    char*  buf;
    size_t buf_len;

    /* Send response with custom headers and body set as the
     * string passed in user context*/
    httpd_resp_set_type(req, "text/html");
    const char* resp_str = (const char*) index_html_start;
    httpd_resp_send(req, resp_str, index_html_end - index_html_start);
    return ESP_OK;
}

static const httpd_uri_t http_get = {
    .uri       = "/get",
    .method    = HTTP_GET,
    .handler   = http_get_handler,
    /* Let's pass response string in user
     * context to demonstrate it's usage */
    .user_ctx  = "Hello World!"
};

/* An HTTP GET handler */
static esp_err_t dht11_handler(httpd_req_t *req)
{
    char res[100]= "";
    float temp = 50.25;
    float humi = 80.91;
    sprintf(res,"{\"temperature\": \"%.02f\", \"humidity\": \"%.02f\"}",temp,humi);
    httpd_resp_send(req, res, strlen(res));
    return ESP_OK;
}

static const httpd_uri_t http_dht11 = {
    .uri       = "/dht11",
    .method    = HTTP_GET,
    .handler   = dht11_handler,
    /* Let's pass response string in user
     * context to demonstrate it's usage */
    .user_ctx  = "Hello World!"
};

/* An HTTP GET handler */
static esp_err_t rgb_handler(httpd_req_t *req)
{
    char res[100]= "";
    size_t buf_len;
    char param[7];
    char val[3] = {0,0,0};
    int r,g,b;
    /* Read URL query string length and allocate memory for length + 1,
     * extra byte for null termination */
    buf_len = httpd_req_get_url_query_len(req) + 1;
    if (buf_len > 1) {
        if (httpd_req_get_url_query_str(req, res, buf_len) == ESP_OK) {
            /* Get value of expected key from query string */
            if (httpd_query_key_value(res, "color", param, sizeof(param)) == ESP_OK) {
                ESP_LOGI(TAG, "Found URL query parameter => query1=%s", param);
                char*s;
                val[0] = param[0];
                val[1] = param[1];
                r = strtol(val, &s, 16);

                val[0] = param[2];
                val[1] = param[3];
                g = strtol(val, &s, 16);

                val[0] = param[4];
                val[1] = param[5];
                b = strtol(val, &s, 16);       

                ESP_LOGI(TAG, "r = %d, g = %d, b = %d", r,g,b);
                p_rgb_handle(r,g,b);                   
            }             
        }
    } 

    httpd_resp_send(req, res, strlen(res));
    return ESP_OK;
}

static const httpd_uri_t http_rgb = {
    .uri       = "/rgb",
    .method    = HTTP_GET,
    .handler   = rgb_handler,
    /* Let's pass response string in user
     * context to demonstrate it's usage */
    .user_ctx  = "Hello World!"
};

/* An HTTP POST handler */
static esp_err_t http_post_handler(httpd_req_t *req)
{
    char buf[100];
    int ret, data_len = req->content_len;

        /* Read the data for the request */
        httpd_req_recv(req, buf,data_len);
        /* Log data received */
        ESP_LOGI(TAG, "Data recv: %.*s", data_len, buf);

    // End response
    httpd_resp_send_chunk(req, NULL, 0);
    return ESP_OK;
}

static const httpd_uri_t http_post = {
    .uri       = "/post",
    .method    = HTTP_POST,
    .handler   = http_post_handler,
    .user_ctx  = NULL
};
"""

# Hàm loại bỏ comment kiểu /* */ và //
def remove_comments(code):
    # Loại bỏ comment kiểu /* */
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    # Loại bỏ comment kiểu //
    code = re.sub(r'//.*', '', code)

    while True:  
        match = re.search(r'{[^{}]*}', code)  
        if( match != None):
            # Loại bỏ nội dung trong các cặp dấu ngoặc nhọn {}
            code = re.sub(r'{[^{}]*}', '', code)
        else:
            break
    return code

# Loại bỏ comment khỏi mã nguồn C
# clean_code = remove_comments(c_code)
# print(clean_code)

def open_file():
    # Viết mã nguồn C vào file tạm thời
    with open('test.c', 'r') as file:
        raw_code = file.read()
        clean_code = remove_comments(raw_code)
        print(clean_code)

open_file()

# Khởi tạo parser và phân tích mã nguồn C đã được làm sạch
# parser = c_parser.CParser()
# ast = parser.parse(clean_code)

# # Lớp Visitor để duyệt AST và tìm tên function cùng các thông tin khác
# class FunctionVisitor(c_ast.NodeVisitor):
#     def visit_FuncDef(self, node):
#         func_name = node.decl.name
#         ret_type = self._get_type(node.decl.type)
#         params = self._get_params(node.decl.type.args)
#         print(f"Found function: {func_name}")
#         print(f"Return type: {ret_type}")
#         print(f"Parameters: {params}")
#         print("-" * 40)
#         # Tiếp tục duyệt các node con nếu cần
#         self.generic_visit(node)

#     def _get_type(self, type_node):
#         if isinstance(type_node, c_ast.TypeDecl):
#             return self._get_type(type_node.type)
#         elif isinstance(type_node, c_ast.IdentifierType):
#             return ' '.join(type_node.names)
#         elif isinstance(type_node, c_ast.PtrDecl):
#             return self._get_type(type_node.type) + '*'
#         return ''

#     def _get_params(self, param_list):
#         if param_list is None:
#             return 'void'
#         params = []
#         for param in param_list.params:
#             param_type = self._get_type(param.type)
#             param_name = param.name
#             params.append(f"{param_type} {param_name}")
#         return ', '.join(params)

# # Khởi tạo visitor và duyệt AST
# visitor = FunctionVisitor()
# visitor.visit(ast)
