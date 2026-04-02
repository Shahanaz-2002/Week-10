# API Contract – Clinical Insight Engine

---

## Overview

This document defines the API contract for the **Clinical Insight Engine**, which provides AI-driven analysis of patient cases.

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

The API accepts patient clinical data including symptoms and optional doctor notes.

---

### Fields

| Field Name   | Type        | Required | Description |
|-------------|--------------|----------|-------------|
| patient_id  | string       |  Yes   | Unique patient identifier |
| symptoms    | list[string] |  Yes   | List of patient symptoms |
| doctor_notes| string       |  No    | Additional clinical notes |
| age         | integer      |  Yes   | Patient age |
| gender      | string       |  Yes   | Patient gender |

---

### Example Request

```json
{
  "patient_id": "P001",
  "symptoms": ["chest pain", "fatigue"],
  "doctor_notes": "Irregular heartbeat observed",
  "age": 54,
  "gender": "male"
}