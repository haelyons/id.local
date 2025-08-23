# Grounded SAM2 API Specification

## Base URL
```
http://localhost:5001
```

## Endpoints

### POST /predict
**Description:** Performs object detection and segmentation using Grounded DINO + SAM2

#### Request Format
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `caption` | `string` | ✅ | - | Text description of objects to detect |
| `images` | `string[]` | ✅ | - | Array of base64-encoded images |
| `box_threshold` | `number` | ❌ | `0.35` | Detection confidence threshold (0.0-1.0) |
| `text_threshold` | `number` | ❌ | `0.25` | Text matching threshold (0.0-1.0) |
| `return_base64_masks` | `boolean` | ❌ | `false` | Return mask images as base64 PNG |

#### Request Body Schema
```json
{
  "caption": "string",
  "images": ["string"],
  "box_threshold": 0.35,
  "text_threshold": 0.25,
  "return_base64_masks": false
}
```

#### Response Format
| Field | Type | Description |
|-------|------|-------------|
| `success` | `boolean` | Operation success status |
| `caption` | `string` | Processed caption (normalized with period) |
| `total_images` | `number` | Number of images processed |
| `results` | `object[]` | Results per image |
| `results[].image_index` | `number` | Index of processed image |
| `results[].image_width` | `number` | Original image width in pixels |
| `results[].image_height` | `number` | Original image height in pixels |
| `results[].annotations` | `object[]` | Detected objects |
| `results[].annotations[].class_name` | `string` | Detected object class |
| `results[].annotations[].bbox` | `number[]` | Bounding box `[x1, y1, x2, y2]` |
| `results[].annotations[].bbox_format` | `string` | Always `"xyxy"` (top-left, bottom-right) |
| `results[].annotations[].confidence` | `number` | Detection confidence (0.0-1.0) |
| `results[].annotations[].mask_score` | `number` | Segmentation quality score (0.0-1.0) |
| `results[].annotations[].segmentation` | `object` | Mask in COCO RLE format |
| `results[].annotations[].segmentation.size` | `number[]` | Mask dimensions `[height, width]` |
| `results[].annotations[].segmentation.counts` | `string` | RLE-encoded mask data |
| `results[].annotations[].mask_base64` | `string` | Optional. Base64 PNG mask image |

#### Response Body Schema
```json
{
  "success": true,
  "caption": "string.",
  "total_images": 1,
  "results": [
    {
      "image_index": 0,
      "image_width": 1920,
      "image_height": 1080,
      "annotations": [
        {
          "class_name": "string",
          "bbox": [123.4, 56.7, 234.5, 345.6],
          "bbox_format": "xyxy",
          "confidence": 0.847,
          "mask_score": 0.923,
          "segmentation": {
            "size": [1080, 1920],
            "counts": "RLE_encoded_string"
          },
          "mask_base64": "base64_png_string"
        }
      ]
    }
  ]
}
```

#### Error Response
```json
{
  "success": false,
  "error": "string"                       // Error description
}
```

### POST /score
**Description:** Alias for `/predict` endpoint (identical functionality)

### GET /
**Description:** API information and available endpoints

#### Response Body
```json
{
  "message": "Grounded SAM2 Local API",
  "status": "running",
  "endpoints": {
    "inference": "/predict",
    "health": "/health"
  }
}
```

### GET /health
**Description:** Health check endpoint

#### Response Body
```json
{
  "status": "healthy",
  "models_loaded": true
}
```

## Data Formats

### Input Images
- **Format:** Base64-encoded strings
- **Supported types:** JPEG, PNG, and other PIL-supported formats
- **Processing:** Images are temporarily saved and processed by Grounding DINO + SAM2

### Bounding Boxes
- **Format:** `[x1, y1, x2, y2]` in `xyxy` format
- **Coordinates:** Absolute pixel coordinates
- **Origin:** Top-left corner (0,0)

### Segmentation Masks
- **RLE Format:** COCO-style Run-Length Encoding
  - Compact binary representation
  - Suitable for storage and transmission
- **Base64 Format:** PNG image as base64 string (optional)
  - White pixels (255) = object mask
  - Black pixels (0) = background
  - Same dimensions as input image

## Processing Pipeline
1. **Input:** Base64 images + text caption
2. **Detection:** Grounding DINO identifies objects matching caption
3. **Segmentation:** SAM2 generates precise masks for detected bounding boxes
4. **Output:** Structured JSON with detections, boxes, and masks

## Error Handling
- Invalid images return per-image error in results array
- Missing required fields return HTTP 400
- Server errors return HTTP 500
- No detections return empty annotations array (not an error)

## Complete Example

### Request
```bash
curl -X POST http://localhost:5001/predict \
  -H "Content-Type: application/json" \
  -d '{
    "caption": "person",
    "images": ["/9j/4AAQSkZJRgABAQEAYABgAAD...base64_image_data..."],
    "box_threshold": 0.35,
    "text_threshold": 0.25,
    "return_base64_masks": true
  }'
```

### Response
```json
{
  "success": true,
  "caption": "person.",
  "total_images": 1,
  "results": [
    {
      "image_index": 0,
      "image_width": 1920,
      "image_height": 1080,
      "annotations": [
        {
          "class_name": "person",
          "bbox": [245.7, 123.4, 456.8, 789.2],
          "bbox_format": "xyxy",
          "confidence": 0.847,
          "mask_score": 0.923,
          "segmentation": {
            "size": [1080, 1920],
            "counts": "nTh52m0N2N2N2N1O1N2N1O1O0O2N1N2N1O1N2N1O1N2O0O2N1N2N..."
          },
          "mask_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        },
        {
          "class_name": "person",
          "bbox": [678.1, 234.5, 890.3, 945.6],
          "bbox_format": "xyxy",
          "confidence": 0.762,
          "mask_score": 0.889,
          "segmentation": {
            "size": [1080, 1920],
            "counts": "mSi63l0M3M2M2M1N2M1N2M1N1N2M1N2M1N2M1N2M1N2M1N2M..."
          },
          "mask_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        }
      ]
    }
  ]
}
```

### Error Response Example
```json
{
  "success": false,
  "error": "No images provided"
}
```

## Performance Notes
- CUDA required
- Models loaded once at server startup
- Processing time scales with image size and number of objects
- Memory usage depends on image resolution and batch size
