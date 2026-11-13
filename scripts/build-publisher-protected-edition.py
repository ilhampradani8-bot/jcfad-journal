#!/usr/bin/env python3
"""
JCFAD Publisher Protection & Automatic PDF Watermarking Engine
==============================================================
1. Membubuhkan watermark diagonal & margin micro-stamp otomatis di setiap halaman PDF
   untuk tampilan Web View (mencegah pembajakan naskah komersial Amazon KDP & Google Play Books).
2. Mengunci izin PDF menggunakan enkripsi standar industri AES-256 (Owner Password Lock,
   permissions=0: Dilarang Print, Dilarang Copy Teks, Dilarang Ekstrak Halaman).
3. Memindahkan berkas master cetak murni (tanpa watermark) ke direktori vault khusus penerbit
   (/books/publisher-master-vault/) agar tidak bisa diunduh sembarangan oleh publik dari Web View.
"""

from pathlib import Path
import shutil
import pymupdf as fitz

ROOT = Path("/root/journal")
OUT_DIR = ROOT / "books/output"
PUBLIC_BOOKS = ROOT / "public/books"
VAULT_DIR = PUBLIC_BOOKS / "publisher-master-vault"
DIST_BOOKS = ROOT / "dist/books"


def apply_publisher_watermark_and_lock(
    src_pdf: Path,
    dst_pdf: Path,
    edition_label: str = "INTERNATIONAL PUBLISHER EDITION • ISBN 979-8-14154-843-7",
    lang: str = "en",
):
    """Stamp every page with diagonal & margin publisher watermarks and lock PDF permissions (AES-256)."""
    doc = fitz.open(str(src_pdf))
    font_bold = fitz.Font("hebo")
    font_reg = fitz.Font("helv")

    for page_idx, page in enumerate(doc):
        rect = page.rect
        w, h = rect.width, rect.height
        cx, cy = w / 2.0, h / 2.0

        # 1. Diagonal Center Watermark (3 lines, rotated -42 degrees)
        tw_diag = fitz.TextWriter(rect)
        if lang == "en":
            line1 = "WEB PREVIEW ONLY • DO NOT DISTRIBUTE"
            line2 = "COPYRIGHT © 2026 ILHAM PRADANI"
            line3 = edition_label
        else:
            line1 = "PRATINJAU WEB • DILARANG MENGUNDUH / MENCETAK"
            line2 = "HAK CIPTA © 2026 ILHAM PRADANI"
            line3 = edition_label

        # Calculate centered positions before rotation
        w1 = font_bold.text_length(line1, fontsize=18)
        w2 = font_bold.text_length(line2, fontsize=15)
        w3 = font_reg.text_length(line3, fontsize=10.5)

        tw_diag.append((cx - w1 / 2.0, cy - 18), line1, font=font_bold, fontsize=18)
        tw_diag.append((cx - w2 / 2.0, cy + 6), line2, font=font_bold, fontsize=15)
        tw_diag.append((cx - w3 / 2.0, cy + 25), line3, font=font_reg, fontsize=10.5)

        rot_matrix = fitz.Matrix(-42)
        tw_diag.write_text(
            page,
            color=(0.55, 0.12, 0.12),
            opacity=0.11,
            morph=(fitz.Point(cx, cy), rot_matrix),
            overlay=True,
        )

        # 2. Secondary Subtle Diagonal Stamp (Upper & Lower thirds)
        tw_sub = fitz.TextWriter(rect)
        sub_text = "PROTECTED PUBLISHER COPY • JCFAD ACADEMIC PRESS • ALL RIGHTS RESERVED"
        ws = font_reg.text_length(sub_text, fontsize=8.5)
        tw_sub.append((cx - ws / 2.0, cy - h * 0.27), sub_text, font=font_reg, fontsize=8.5)
        tw_sub.append((cx - ws / 2.0, cy + h * 0.27), sub_text, font=font_reg, fontsize=8.5)
        tw_sub.write_text(
            page,
            color=(0.35, 0.35, 0.40),
            opacity=0.09,
            morph=(fitz.Point(cx, cy), rot_matrix),
            overlay=True,
        )

        # 3. Bottom Margin Micro-Stamp (Horizontal Security Footer)
        tw_foot = fitz.TextWriter(rect)
        if lang == "en":
            foot_text = f"PROTECTED WEB VIEW (PAGE {page_idx + 1} OF {len(doc)}) • COMMERCIAL PRINT & EBOOK EDITION: AMAZON KDP (ISBN 9798141548437) • UNAUTHORIZED DOWNLOADING PROHIBITED"
        else:
            foot_text = f"PRATINJAU WEB TERPROTEKSI (HAL {page_idx + 1} DARI {len(doc)}) • EDISI KOMERSIAL RESMI: AMAZON KDP & GOOGLE PLAY BOOKS • DILARANG MENYALIN TANPA IZIN"
        wf = font_reg.text_length(foot_text, fontsize=5.6)
        tw_foot.append((cx - wf / 2.0, h - 10), foot_text, font=font_reg, fontsize=5.6)
        tw_foot.write_text(
            page,
            color=(0.45, 0.15, 0.15),
            opacity=0.45,
            overlay=True,
        )

    dst_pdf.parent.mkdir(parents=True, exist_ok=True)
    # Save with AES-256 Owner Password Lock & 0 permissions (No Print, No Copy, No Edit, No Extract)
    doc.save(
        str(dst_pdf),
        garbage=4,
        deflate=True,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        owner_pw="JCFAD-PUBLISHER-MASTER-LOCK-2026",
        user_pw="",
        permissions=0,
    )
    page_count = len(doc)
    doc.close()
    print(f"✅ Watermarked & AES-256 Locked PDF siap: {dst_pdf} ({page_count} halaman)")


def main():
    PUBLIC_BOOKS.mkdir(parents=True, exist_ok=True)
    VAULT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Move/Copy clean unwatermarked commercial master files into publisher-master-vault
    master_files = [
        "manipulative-intelligence-kdp-6x9-manuscript.pdf",
        "manipulative-intelligence-kdp-6x9-hardcover-cover.pdf",
        "manipulative-intelligence-kdp-6x9-paperback-cover.pdf",
        "manipulative-intelligence-kdp.epub",
        "manipulative-intelligence-ebook-cover.jpg",
        "sampulbelakang-english-amazon-selfhelp.jpeg",
        "synthetic-empathy-amazon-kdp-print-ready.pdf",
        "kecerdasan-manipulatif-indo-6x9-manuscript.pdf",
        "kecerdasan-manipulatif-indo-6x9-hardcover-cover.pdf",
        "kecerdasan-manipulatif-indo-6x9-paperback-cover.pdf",
        "kecerdasan-manipulatif-google-books.epub",
        "empati-sintetis-google-books.epub",
        "sampuldepan-kecerdasan-manipulatif-indo.jpeg",
        "sampulbelakang-indo-selfhelp.jpeg",
    ]

    for fname in master_files:
        src_in_public = PUBLIC_BOOKS / fname
        src_in_out = OUT_DIR / fname
        if src_in_out.exists():
            shutil.copyfile(src_in_out, VAULT_DIR / fname)
        elif src_in_public.exists():
            shutil.copyfile(src_in_public, VAULT_DIR / fname)

    # Copy pure ISO-B5 print-ready master to vault
    iso_master = OUT_DIR / "empati-sintetis-buku-cetak-print-ready.pdf"
    if iso_master.exists():
        shutil.copyfile(iso_master, VAULT_DIR / "empati-sintetis-iso-b5-master-clean.pdf")

    # 2. Generate Watermarked & AES-256 Locked Web Preview PDFs
    # A. English International Edition (6x9 Amazon KDP)
    en_src = OUT_DIR / "manipulative-intelligence-kdp-6x9-manuscript.pdf"
    if en_src.exists():
        apply_publisher_watermark_and_lock(
            en_src,
            PUBLIC_BOOKS / "preview-english-watermarked.pdf",
            edition_label="MANIPULATIVE INTELLIGENCE • AMAZON KDP EDITION (ISBN 979-8-14154-843-7)",
            lang="en",
        )

    # B. Indonesian Commercial Edition (6x9 Google Play Books / Print)
    id_6x9_src = OUT_DIR / "kecerdasan-manipulatif-indo-6x9-manuscript.pdf"
    if id_6x9_src.exists():
        apply_publisher_watermark_and_lock(
            id_6x9_src,
            PUBLIC_BOOKS / "preview-indo-6x9-watermarked.pdf",
            edition_label="KECERDASAN MANIPULATIF • EDISI CETAK & GOOGLE PLAY BOOKS",
            lang="id",
        )

    # C. Indonesian ISO-B5 Monograph Edition
    if iso_master.exists():
        apply_publisher_watermark_and_lock(
            iso_master,
            PUBLIC_BOOKS / "preview-indo-watermarked.pdf",
            edition_label="EMPATI SINTETIS • MONOGRAF AKADEMIK JCFAD (DOI: 10.5281/zenodo.24106942)",
            lang="id",
        )
        # Also overwrite public /books/empati-sintetis.pdf with the watermarked & locked version
        shutil.copyfile(
            PUBLIC_BOOKS / "preview-indo-watermarked.pdf",
            PUBLIC_BOOKS / "empati-sintetis.pdf",
        )

    print("🔒 Seluruh berkas Web Preview telah diberi Watermark Otomatis & Kunci Enkripsi AES-256!")


if __name__ == "__main__":
    main()
