import re
import customtkinter as ctk
from tkinter import filedialog

# ----------------------------------------------------------------------------
# THEME
# ----------------------------------------------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG_MAIN = "#0a0e14"
BG_PANEL = "#0f1621"
BG_FIELD = "#0b1119"
ACCENT = "#00e5ff"       # cyan
ACCENT_2 = "#7c5cff"     # violet
ACCENT_SOFT = "#12202b"
SUCCESS = "#00ff9c"
DANGER = "#ff4d6d"
TEXT_MAIN = "#e6f1ff"
TEXT_DIM = "#5c7a94"
BORDER = "#1c2a38"

URL_REGEX = re.compile(r'https?://[^\s<>"\'()]+', re.IGNORECASE)

FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_SUB = ("Segoe UI", 11)
FONT_LABEL = ("Segoe UI", 12, "bold")
FONT_MONO = ("Consolas", 12)
FONT_BTN = ("Segoe UI", 12, "bold")
FONT_STAT = ("Consolas", 12, "bold")


class GlowButton(ctk.CTkButton):
    """A button with a quick color-flash used for transient feedback (e.g. Copied!)."""

    def flash(self, text, color, revert_text, revert_color, ms=1200):
        self.configure(text=text, fg_color=color)
        self.after(ms, lambda: self.configure(text=revert_text, fg_color=revert_color))


class URLExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("URL Extractor Pro")
        self.root.geometry("1280x860")
        self.root.minsize(980, 680)
        self.root.configure(fg_color=BG_MAIN)

        self._build_header()
        self._build_input_section()
        self._build_action_bar()
        self._build_stats_bar()
        self._build_output_section()

    # ------------------------------------------------------------------
    # HEADER
    # ------------------------------------------------------------------
    def _build_header(self):
        header = ctk.CTkFrame(self.root, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(24, 10))

        title_row = ctk.CTkFrame(header, fg_color="transparent")
        title_row.pack(fill="x")

        accent_bar = ctk.CTkFrame(title_row, fg_color=ACCENT, width=5, height=40, corner_radius=3)
        accent_bar.pack(side="left", padx=(0, 12))

        title_col = ctk.CTkFrame(title_row, fg_color="transparent")
        title_col.pack(side="left", fill="x")

        ctk.CTkLabel(
            title_col, text="URL EXTRACTOR PRO", font=FONT_TITLE, text_color=TEXT_MAIN
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_col,
            text="Extract, dedupe & group links from raw text",
            font=FONT_SUB,
            text_color=TEXT_DIM,
        ).pack(anchor="w")

    # ------------------------------------------------------------------
    # INPUT SECTION
    # ------------------------------------------------------------------
    def _build_input_section(self):
        panel = ctk.CTkFrame(self.root, fg_color=BG_PANEL, corner_radius=14, border_width=1, border_color=BORDER)
        panel.pack(fill="both", expand=True, padx=28, pady=8)

        row = ctk.CTkFrame(panel, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(16, 6))

        ctk.CTkLabel(row, text="INPUT TEXT", font=FONT_LABEL, text_color=ACCENT).pack(side="left")

        btn_group = ctk.CTkFrame(row, fg_color="transparent")
        btn_group.pack(side="right")

        ctk.CTkButton(
            btn_group, text="Paste", width=90, height=30, font=FONT_BTN,
            fg_color=ACCENT_SOFT, hover_color=BORDER, text_color=ACCENT,
            border_width=1, border_color=ACCENT, corner_radius=8,
            command=self.paste_input,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            btn_group, text="Clear", width=90, height=30, font=FONT_BTN,
            fg_color=ACCENT_SOFT, hover_color=BORDER, text_color=TEXT_DIM,
            border_width=1, border_color=BORDER, corner_radius=8,
            command=self.clear_input,
        ).pack(side="left", padx=4)

        self.input_box = ctk.CTkTextbox(
            panel, height=200, font=FONT_MONO, fg_color=BG_FIELD,
            text_color=TEXT_MAIN, corner_radius=10, border_width=1,
            border_color=BORDER, wrap="word",
        )
        self.input_box.pack(fill="both", expand=True, padx=18, pady=(0, 16))

    # ------------------------------------------------------------------
    # ACTION BAR
    # ------------------------------------------------------------------
    def _build_action_bar(self):
        bar = ctk.CTkFrame(self.root, fg_color="transparent")
        bar.pack(fill="x", padx=28, pady=4)

        actions = [
            ("Extract URLs", ACCENT, self.extract_urls),
            ("Remove Duplicates", ACCENT_2, self.remove_duplicates),
            ("Group URLs Only", ACCENT_2, self.group_urls),
            ("Export TXT", TEXT_DIM, self.export_txt),
        ]

        for text, color, cmd in actions:
            ctk.CTkButton(
                bar, text=text, height=38, font=FONT_BTN, corner_radius=9,
                fg_color=BG_FIELD, hover_color=ACCENT_SOFT, text_color=color,
                border_width=1, border_color=color, command=cmd,
            ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            bar, text="Clear All", height=38, font=FONT_BTN, corner_radius=9,
            fg_color=BG_FIELD, hover_color="#2a0f18", text_color=DANGER,
            border_width=1, border_color=DANGER, command=self.clear_all,
        ).pack(side="right")

    # ------------------------------------------------------------------
    # STATS BAR
    # ------------------------------------------------------------------
    def _build_stats_bar(self):
        stats_panel = ctk.CTkFrame(self.root, fg_color=BG_PANEL, corner_radius=12, border_width=1, border_color=BORDER)
        stats_panel.pack(fill="x", padx=28, pady=8)

        inner = ctk.CTkFrame(stats_panel, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=12)

        self.stat_found = self._make_stat(inner, "URLs FOUND", "0", ACCENT)
        self.stat_unique = self._make_stat(inner, "UNIQUE URLS", "0", SUCCESS)
        self.stat_groups = self._make_stat(inner, "UNIQUE GROUPS", "0", ACCENT_2)

    def _make_stat(self, parent, label, value, color):
        cell = ctk.CTkFrame(parent, fg_color="transparent")
        cell.pack(side="left", padx=(0, 40))
        ctk.CTkLabel(cell, text=label, font=("Segoe UI", 10), text_color=TEXT_DIM).pack(anchor="w")
        val_label = ctk.CTkLabel(cell, text=value, font=FONT_STAT, text_color=color)
        val_label.pack(anchor="w")
        return val_label

    # ------------------------------------------------------------------
    # OUTPUT SECTION
    # ------------------------------------------------------------------
    def _build_output_section(self):
        panel = ctk.CTkFrame(self.root, fg_color=BG_PANEL, corner_radius=14, border_width=1, border_color=BORDER)
        panel.pack(fill="both", expand=True, padx=28, pady=(8, 24))

        row = ctk.CTkFrame(panel, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(16, 6))

        ctk.CTkLabel(row, text="RESULTS", font=FONT_LABEL, text_color=ACCENT).pack(side="left")

        self.copy_btn = GlowButton(
            row, text="Copy All", width=110, height=30, font=FONT_BTN,
            fg_color=ACCENT_SOFT, hover_color=BORDER, text_color=SUCCESS,
            border_width=1, border_color=SUCCESS, corner_radius=8,
            command=self.copy_all,
        )
        self.copy_btn.pack(side="right")

        self.output_box = ctk.CTkTextbox(
            panel, font=FONT_MONO, fg_color=BG_FIELD, text_color=TEXT_MAIN,
            corner_radius=10, border_width=1, border_color=BORDER, wrap="word",
        )
        self.output_box.pack(fill="both", expand=True, padx=18, pady=(0, 16))

    # ------------------------------------------------------------------
    # LOGIC
    # ------------------------------------------------------------------
    def update_stats(self, urls):
        unique_urls = len(dict.fromkeys(urls))
        groups = [g for g in (self.get_group_url(u) for u in urls) if g]
        unique_groups = len(dict.fromkeys(groups))

        self.stat_found.configure(text=str(len(urls)))
        self.stat_unique.configure(text=str(unique_urls))
        self.stat_groups.configure(text=str(unique_groups))

    def get_urls(self):
        text = self.input_box.get("1.0", "end")
        return URL_REGEX.findall(text)

    def get_group_url(self, url):
        patterns = [
            r'(https?://(?:www\.)?facebook\.com/groups/\d+/)',
            r'(https?://(?:www\.)?facebook\.com/groups/[^/]+/)',
        ]
        for p in patterns:
            m = re.search(p, url, re.I)
            if m:
                return m.group(1)
        return None

    def extract_urls(self):
        urls = self.get_urls()
        self.output_box.delete("1.0", "end")
        self.output_box.insert("end", "\n".join(urls))
        self.update_stats(urls)

    def remove_duplicates(self):
        lines = [x.strip() for x in self.output_box.get("1.0", "end").splitlines() if x.strip()]
        unique = list(dict.fromkeys(lines))
        self.output_box.delete("1.0", "end")
        self.output_box.insert("end", "\n".join(unique))

    def group_urls(self):
        urls = self.get_urls()
        groups = [g for g in (self.get_group_url(u) for u in urls) if g]
        groups = list(dict.fromkeys(groups))

        self.output_box.delete("1.0", "end")
        self.output_box.insert("end", "\n".join(groups))
        self.update_stats(urls)

    def paste_input(self):
        try:
            clip = self.root.clipboard_get()
        except Exception:
            return
        if clip:
            self.input_box.insert("insert", clip)

    def copy_all(self):
        txt = self.output_box.get("1.0", "end").strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(txt)
        # inline feedback instead of a popup dialog
        self.copy_btn.flash(
            text="Copied ✓", color=SUCCESS,
            revert_text="Copy All", revert_color=ACCENT_SOFT,
        )

    def export_txt(self):
        file = filedialog.asksaveasfilename(defaultextension=".txt")
        if not file:
            return
        with open(file, "w", encoding="utf-8") as f:
            f.write(self.output_box.get("1.0", "end"))

    def clear_input(self):
        self.input_box.delete("1.0", "end")

    def clear_all(self):
        self.input_box.delete("1.0", "end")
        self.output_box.delete("1.0", "end")
        self.stat_found.configure(text="0")
        self.stat_unique.configure(text="0")
        self.stat_groups.configure(text="0")


if __name__ == "__main__":
    root = ctk.CTk()
    URLExtractor(root)
    root.mainloop()
