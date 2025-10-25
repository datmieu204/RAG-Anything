# RAGAnything với Ollama - Hướng dẫn sử dụng

## Clone repository

- Tải uv

- Clone về local:

```bash
git clone https://github.com/datmieu204/RAG-Anything.git
cd RAG-Anything
```

- Đồng bộ uv:

```bash
uv sync
```

- Đồng bộ submodule:

```bash
uv sync --all-extras 
```

- Check MinerU installation:

```bash
# Verify installation
mineru --version

# Check if properly configured
python -c "from raganything import RAGAnything; rag = RAGAnything(); print('✅ MinerU installed properly' if rag.check_parser_installation() else '❌ MinerU installation issue')"
```

## Giới thiệu

File `raganything_example.py` đã được tinh chỉnh để sử dụng các mô hình LLM local thông qua Ollama thay vì OpenAI API.

## Yêu cầu

### 1. Cài đặt Ollama

Tải và cài đặt Ollama từ [https://ollama.ai](https://ollama.ai)

### 2. Cài đặt các mô hình cần thiết

Dựa trên các model bạn đã có:

```bash
# Kiểm tra các model đã cài
ollama list

# Các model cần thiết:
# ✅ mistral:latest - LLM chính (4.4 GB)
# ✅ llava:latest - Vision model cho xử lý hình ảnh (4.7 GB)
# ✅ bge-m3:latest - Embedding model (1.2 GB)
```

Nếu chưa có, cài đặt bằng:

```bash
ollama pull mistral:latest
ollama pull llava:latest
ollama pull bge-m3:latest
```

### 3. Khởi động Ollama server

Ollama thường tự động khởi động khi cài đặt. Kiểm tra bằng cách:

```bash
# Windows PowerShell
curl http://localhost:11434/v1/models
```

Nếu chưa chạy, khởi động Ollama từ Start Menu hoặc command line.

## Cấu hình

### Option 1: Sử dụng file .env

1. Copy file cấu hình mẫu:

```powershell
Copy-Item .env.ollama .env
```

2. Chỉnh sửa `.env` nếu cần (thường không cần thiết với cấu hình mặc định)

### Option 2: Sử dụng biến môi trường

```powershell
$env:OLLAMA_LLM_MODEL="mistral:latest"
$env:OLLAMA_VISION_MODEL="llava:latest"
$env:OLLAMA_EMBEDDING_MODEL="bge-m3:latest"
$env:OLLAMA_BASE_URL="http://localhost:11434/v1"
$env:EMBEDDING_DIM="1024"
```

## Cách sử dụng

### 1. Xử lý một file đơn

```powershell
# Cú pháp cơ bản
python examples/raganything_example.py "đường/dẫn/tới/file.pdf"
python examples/raganything_example.py data/sample.pdf

# Với các tùy chọn
python examples/raganything_example.py "e:\Documents\sample.pdf" -w "./my_rag_storage" -o "./my_output"
```

### 2. Các tham số dòng lệnh

```
raganything_example.py [-h] [--working_dir WORKING_DIR] [--output OUTPUT] [--parser PARSER] file_path

Positional arguments:
  file_path             Đường dẫn tới file cần xử lý

Optional arguments:
  -h, --help            Hiển thị trợ giúp
  -w, --working_dir     Thư mục lưu trữ RAG (mặc định: ./rag_storage)
  -o, --output          Thư mục output (mặc định: ./output)
  --parser              Parser sử dụng: mineru hoặc docling (mặc định: mineru)
```

### 3. Ví dụ cụ thể

```powershell
# Xử lý file PDF
python examples/raganything_example.py "e:\RAG-Anything\data\sample.pdf"

# Xử lý file Word với output tùy chỉnh
python examples/raganything_example.py "e:\Documents\report.docx" -o "./output/report"

# Sử dụng docling parser
python examples/raganything_example.py "e:\Documents\presentation.pptx" --parser docling

# Chỉ định working directory khác
python examples/raganything_example.py "e:\data\research.pdf" -w "./rag_storage_research"
```

## Các model Ollama được sử dụng

| Model              | Mục đích                  | Kích thước | Cấu hình                 |
| ------------------ | ------------------------- | ---------- | ------------------------ |
| **mistral:latest** | LLM chính cho văn bản     | 4.4 GB     | `OLLAMA_LLM_MODEL`       |
| **llava:latest**   | Vision model cho hình ảnh | 4.7 GB     | `OLLAMA_VISION_MODEL`    |
| **bge-m3:latest**  | Embedding (1024 chiều)    | 1.2 GB     | `OLLAMA_EMBEDDING_MODEL` |

## Tính năng

Script này hỗ trợ:

✅ **Xử lý văn bản thuần túy** - Sử dụng `mistral:latest`

- Trích xuất text từ documents
- Phân tích nội dung
- Trả lời câu hỏi dựa trên context

✅ **Xử lý đa phương thức (multimodal)** - Sử dụng `llava:latest`

- Phân tích hình ảnh trong document
- Trích xuất thông tin từ bảng biểu
- Hiểu công thức toán học (equations)

✅ **Vector embedding** - Sử dụng `bge-m3:latest`

- Tạo embeddings cho semantic search
- Tìm kiếm tương đồng
- Retrieval hiệu quả

## Ví dụ query sau khi xử lý

Sau khi xử lý document, script sẽ tự động thực hiện các query mẫu:

### 1. Text queries

```python
"What is the main content of the document?"
"What are the key topics discussed?"
```

### 2. Multimodal query với table

```python
"Compare this performance data with any similar results mentioned in the document"
```

### 3. Multimodal query với equation

```python
"Explain this formula and relate it to any mathematical concepts in the document"
```

## Xử lý lỗi thường gặp

### Lỗi: Connection refused

```
❌ Nguyên nhân: Ollama server chưa chạy
✅ Giải pháp: Khởi động Ollama từ Start Menu hoặc chạy `ollama serve`
```

### Lỗi: Model not found

```
❌ Nguyên nhân: Model chưa được cài đặt
✅ Giải pháp: Chạy `ollama pull <model_name>`
```

### Lỗi: Out of memory

```
❌ Nguyên nhân: Không đủ RAM/VRAM cho model
✅ Giải pháp:
   - Sử dụng model nhỏ hơn (ví dụ: mistral:7b thay vì mistral:latest)
   - Đóng các ứng dụng khác
   - Giảm số lượng concurrent processing
```

### Embedding dimension mismatch

```
❌ Nguyên nhân: EMBEDDING_DIM không khớp với model
✅ Giải pháp:
   - bge-m3 sử dụng 1024 dimensions
   - Đảm bảo EMBEDDING_DIM=1024 trong .env
```

## Logs và Debug

Logs được lưu tại: `raganything_example.log`

Để enable verbose debug:

```powershell
$env:VERBOSE="true"
python raganything_example.py "file.pdf"
```

## So sánh với OpenAI

| Tính năng    | OpenAI (cũ)           | Ollama (mới)           |
| ------------ | --------------------- | ---------------------- |
| **Chi phí**  | Trả phí theo token    | Hoàn toàn miễn phí     |
| **Riêng tư** | Dữ liệu gửi lên cloud | 100% local, an toàn    |
| **Tốc độ**   | Phụ thuộc internet    | Chạy local, nhanh hơn  |
| **Yêu cầu**  | API key               | RAM/VRAM đủ            |
| **Model**    | gpt-4o-mini, gpt-4o   | mistral, llava, bge-m3 |

## Performance Tips

1. **GPU Acceleration**: Ollama tự động sử dụng GPU nếu có
2. **Model Size**: Sử dụng model nhỏ hơn nếu RAM hạn chế
3. **Batch Processing**: Giảm `MAX_CONCURRENT_FILES` nếu hết memory
4. **Cache**: Kết quả được cache để tái sử dụng

## Tài liệu tham khảo

- [Ollama Documentation](https://github.com/ollama/ollama)
- [RAG-Anything Documentation](../README.md)
- [BGE-M3 Model](https://huggingface.co/BAAI/bge-m3)
- [Mistral Model](https://ollama.ai/library/mistral)
- [LLaVA Model](https://ollama.ai/library/llava)

## Support

Nếu gặp vấn đề, hãy:

1. Kiểm tra logs tại `raganything_example.log`
2. Chạy với `VERBOSE=true` để xem chi tiết
3. Verify Ollama đang chạy: `curl http://localhost:11434/v1/models`
4. Kiểm tra models đã cài: `ollama list`
