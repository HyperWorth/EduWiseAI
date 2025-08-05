import os
from google import genai
from google.genai import types
from logger import logger  # logger'ı ekledik
import streamlit as st
# Ortak istemci

client = genai.Client(
    api_key=(st.secrets["GEMINI_API_KEY"]),
)


def call_gemini_json_response(prompt_text: str, system_instruction: str, output_schema: dict, model_name: str = "gemini-2.5-flash-lite") -> str:
    """
    Gemini API ile JSON formatında çıktı üretir.
    """
    try:
        logger.info(f"call_gemini_json_response çağrıldı, model: {model_name}")

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt_text)],
            )
        ]

        system_instructions = [
            types.Part.from_text(text=system_instruction)
        ]

        schema = convert_dict_to_schema(output_schema)

        generate_content_config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            system_instruction=system_instructions,
        )

        response_chunks = client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=generate_content_config,
        )

        output = ""
        for chunk in response_chunks:
            output += chunk.text

        logger.info("call_gemini_json_response başarıyla tamamlandı")
        return output

    except Exception as e:
        logger.error(f"call_gemini_json_response sırasında hata oluştu: {e}", exc_info=True)
        raise


def convert_dict_to_schema(schema_dict: dict) -> genai.types.Schema:
    """
    Python dict şemasını Gemini Schema formatına dönüştürür.
    """
    try:
        def recursive_convert(d):
            schema_type = d.get("type")
            if schema_type == "object":
                return genai.types.Schema(
                    type=genai.types.Type.OBJECT,
                    required=d.get("required", []),
                    properties={
                        k: recursive_convert(v)
                        for k, v in d.get("properties", {}).items()
                    }
                )
            elif schema_type == "array":
                return genai.types.Schema(
                    type=genai.types.Type.ARRAY,
                    items=recursive_convert(d.get("items"))
                )
            else:
                return genai.types.Schema(
                    type=getattr(genai.types.Type, schema_type.upper())
                )

        return recursive_convert(schema_dict)

    except Exception as e:
        logger.error(f"convert_dict_to_schema sırasında hata oluştu: {e}", exc_info=True)
        raise
