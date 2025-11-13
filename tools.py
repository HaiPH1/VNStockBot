from google.genai import types

tool_call = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="get_shareholders",
                description="Tra cứu thông tin Cổ đông lớn",
                parameters={
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Mã chứng khoán, ví dụ 'FPT', 'VNM', 'HPG'."
                        }
                    },
                    "required": ["ticker"]
                }
            ),
    
            types.FunctionDeclaration(
                name="get_officers",
                description="Tra cứu thông tin Ban lãnh đạo, có thể lọc theo trạng thái làm việc.",
                parameters={
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Mã chứng khoán, ví dụ 'FPT', 'VNM', 'HPG'."},
                        "filter_by": {
                            "type": "string",
                            "enum": ["working", "resigned", "all"],
                            "description": "Trạng thái lãnh đạo: 'working' - đang làm việc, 'resigned' - đã nghỉ, 'all' - tất cả."
                        }
                    },
                    "required": ["ticker"]
                }
            ),


            types.FunctionDeclaration(
                name="get_subsidiaries",
                description="Tra cứu thông tin Công ty con",
                parameters={
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Mã chứng khoán, ví dụ 'FPT', 'VNM', 'HPG'."
                        }
                    },
                    "required": ["ticker"]
                }
            ),
            types.FunctionDeclaration(
                name="get_historical_price",
                description="Lấy dữ liệu giá lịch sử (open, high, low, close, volume) theo ngày, tuần, tháng hoặc khoảng thời gian tương đối.",
                parameters={
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "array",               
                            "items": {"type": "string"},  
                            "description": "Một hoặc nhiều mã chứng khoán, ví dụ ['HPG', 'VCB']"
                        },
                        "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                        "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                        "time_range": {"type": "string", "description": "Khoảng thời gian tương đối, ví dụ '7d', '1m', '1y', 'ytd'."},
                        "month": {
                            "type": "integer",
                            "description": "Tháng trong năm (1–12). Dùng khi câu hỏi kiểu 'từ đầu tháng 11'."
                        },
                        "resolution": {
                            "type": "string",
                            "enum": ["1d", "1w", "1m"],
                            "description": "Độ phân giải dữ liệu: theo ngày (1d), tuần (1w), hoặc tháng (1m)."
                        }
                    },
                    "required": ["ticker"]
                }
            )

        ]
    )
]
