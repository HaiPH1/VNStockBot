# Cài đặt

```bash
pip install -r requirements.txt
```

# Run API

Tạo file .env như .env-example. Điền Google API của bạn vào file. (API key có khả năng sử dụng Gemini API)

Sau đó:

```bash
uvicorn vnstock_api:app --reload
```

# Test API

```bash
python tests/test_runner.py;
```