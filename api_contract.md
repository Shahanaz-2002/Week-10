# API Contract – CCMS Insight Engine

---

## Overview

This document defines the API contract for the **CCMS Insight Engine**, which provides AI-driven analysis of customer complaints.

It specifies:
- API endpoint details
- Request format (input schema)
- Response format (output schema)
- Error handling structure

This contract ensures seamless integration with the **CCMS Spring Boot backend**.

---

## 🔹 1. Endpoint Details

- **URL:** `/analyze-case`
- **Method:** `POST`
- **Content-Type:** `application/json`

---

## 🔹 2. Request Schema (Input)

### Description

The API accepts customer complaint data, primarily driven by a detailed case description, to find similar historical resolutions.

---

### Fields

| Field Name       | Type    | Required | Description                                   |
|------------------|---------|----------|-----------------------------------------------|
| customer_id      | string  | Yes      | Unique customer identifier                    |
| case_description | string  | Yes      | Detailed description of the issue or complaint|
| location         | string  | No       | Location associated with the complaint        |
| category         | string  | No       | Optional pre-assigned category                |

---

### Example Request

```json
{
  "customer_id": "CUST-8992",
  "case_description": "The login portal crashes every time I try to reset my password.",
  "location": "New York",
  "category": "Technical Issue"
}