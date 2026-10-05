"""
Adaptador de motor OCR de alta precisión mediante RapidOCR ONNX Runtime.
Implementa el puerto IOCREngine con soporte para coordenadas tipográficas de 72 DPI (Fase 2.0).
"""

from typing import List, Optional, Tuple
import pymupdf

from app.domain.ports import IOCREngine, OCRTextBlock


class RapidOcrEngine(IOCREngine):
    """
    Motor OCR local autosuficiente basado en redes neuronales livianas (ONNX Runtime).
    No requiere dependencias de sistema adicionales ni Tesseract externo.
    Convierte píxeles de rasterizado directamente a puntos tipográficos (72 DPI).
    """

    def __init__(self, default_dpi: int = 150) -> None:
        self.default_dpi = default_dpi
        self._engine: Optional[object] = None

    def _get_engine(self) -> object:
        """Inicialización perezosa (lazy) del modelo ONNX de RapidOCR."""
        if self._engine is None:
            try:
                from rapidocr_onnxruntime import RapidOCR
                self._engine = RapidOCR()
            except ImportError as e:
                raise RuntimeError(
                    "rapidocr_onnxruntime no está instalado en el entorno. "
                    "Ejecute 'pip install rapidocr_onnxruntime' para habilitar el soporte de OCR."
                ) from e
        return self._engine

    def extract_page_ocr(
        self,
        pdf_path: str,
        page_number: int,
        dpi: Optional[int] = None,
    ) -> Tuple[str, List[OCRTextBlock], float, float]:
        """
        Renderiza la página indicada a alta resolución, ejecuta detección y reconocimiento
        neuronal de texto y mapea los cuadros delimitadores al sistema tipográfico estándar (72 DPI).
        
        Args:
            pdf_path: Ruta absoluta o relativa al archivo PDF.
            page_number: Número de página (1-indexed).
            dpi: Resolución de rasterizado (por defecto 150 DPI).

        Returns:
            Tuple con (texto_completo, lista_bloques_ocr, page_width_pt, page_height_pt).
        """
        target_dpi = dpi or self.default_dpi
        scale = 72.0 / float(target_dpi)

        doc = pymupdf.open(pdf_path)
        try:
            if page_number < 1 or page_number > len(doc):
                raise ValueError(f"Página inválida {page_number}. El documento tiene {len(doc)} páginas.")

            page = doc[page_number - 1]
            page_width_pt = float(page.rect.width)
            page_height_pt = float(page.rect.height)

            # Rasterizar a imagen para OCR
            pix = page.get_pixmap(dpi=target_dpi)
            img_bytes = pix.tobytes("png")
        finally:
            doc.close()

        engine = self._get_engine()
        result, _ = engine(img_bytes)

        if not result:
            return "", [], page_width_pt, page_height_pt

        blocks: List[OCRTextBlock] = []
        for item in result:
            dt_boxes, text, confidence = item
            if not text or not text.strip():
                continue

            # dt_boxes contiene 4 vértices del polígono [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            xs = [pt[0] for pt in dt_boxes]
            ys = [pt[1] for pt in dt_boxes]

            x0 = min(xs) * scale
            y0 = min(ys) * scale
            x1 = max(xs) * scale
            y1 = max(ys) * scale

            # Ajustar límites a las dimensiones físicas de la página
            x0 = max(0.0, min(x0, page_width_pt))
            y0 = max(0.0, min(y0, page_height_pt))
            x1 = max(0.0, min(x1, page_width_pt))
            y1 = max(0.0, min(y1, page_height_pt))

            blocks.append(
                OCRTextBlock(
                    text=text.strip(),
                    confidence=float(confidence),
                    x0=round(x0, 2),
                    y0=round(y0, 2),
                    x1=round(x1, 2),
                    y1=round(y1, 2),
                )
            )

        # Ordenar lectura canónica: superior a inferior, izquierda a derecha
        blocks.sort(key=lambda b: (round(b.y0 / 12) * 12, b.x0))

        full_text = "\n".join(b.text for b in blocks)
        return full_text, blocks, page_width_pt, page_height_pt
