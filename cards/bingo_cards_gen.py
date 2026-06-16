"""
Award-winning Bingo card generator.

Generates unique 5x5 BINGO cards (B 1-15, I 16-30, N 31-45 w/ free centre,
G 46-60, O 61-75) and writes a print-ready HTML document laid out two cards
per A4 page with cut guides. Open the HTML in a browser and "Print to PDF".

Usage:
    python bingo_cards_gen.py [num_cards] [output.html]

Defaults: 30 cards -> bingo_cards.html (next to this script).
The cards are self-contained: no external images or fonts are required
(web fonts are pulled in when online, with graceful system-font fallbacks).
"""

import os
import sys
import random

# ----------------------------- configuration -----------------------------
NUM_CARDS = 30
EVENT_NAME = "BINGO NIGHT"
TAGLINE = "Mark a line to win"
SEED = 1337  # fixed seed => reproducible deck; set to None for fresh decks

# Column accent colours (B, I, N, G, O) — printed exactly.
COLUMNS = [
    ("B", "#e0294b", "#fde7ec"),  # crimson
    ("I", "#1f7ae0", "#e6f1fd"),  # blue
    ("N", "#15a37f", "#e4f6f1"),  # emerald
    ("G", "#e8a200", "#fdf3da"),  # amber/gold
    ("O", "#7b3ff2", "#efe8fe"),  # violet
]

# ------------------------------- templates --------------------------------
STYLE = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Playfair+Display:wght@700;800;900&display=swap');

  :root {
    --ink: #1d2330;
    --paper: #ffffff;
    --b: #e0294b; --i: #1f7ae0; --n: #15a37f; --g: #e8a200; --o: #7b3ff2;
  }
  * { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }

  html, body {
    margin: 0; padding: 0;
    font-family: "Fredoka", "Segoe UI", system-ui, sans-serif;
    color: var(--ink);
    background: #d7dae2;            /* desk colour around the sheets (screen only) */
  }

  /* one printed sheet = two cards */
  .page {
    width: 210mm; height: 297mm;
    margin: 10mm auto;             /* screen spacing; collapses in print */
    padding: 11mm 12mm;
    background: var(--paper);
    box-shadow: 0 6px 26px rgba(0,0,0,.22);
    display: flex; flex-direction: column;
    gap: 9mm;
  }

  /* dashed fold/cut guide between the two cards */
  .cutline {
    border: none; border-top: 1.3px dashed #b8bcc8;
    position: relative; margin: 0;
  }
  .cutline::after {
    content: "\\2702"; position: absolute; left: -2mm; top: -8px;
    font-size: 13px; color: #b8bcc8;
  }

  /* ------------------------------- card -------------------------------- */
  .card {
    flex: 1; position: relative; overflow: hidden;
    border-radius: 16px; padding: 7mm 7mm 6mm;
    background:
      radial-gradient(120% 90% at 0% 0%, #ffffff 0%, #fbfbff 55%, #f4f5fb 100%);
    border: 2px solid #e7e9f2;
    box-shadow: inset 0 0 0 6px #ffffff, inset 0 0 0 7px #ececf4,
                0 2px 10px rgba(20,24,40,.06);
    display: flex; flex-direction: column;
  }
  /* gilt corner flourishes (card-suit motif) */
  .card .suit {
    position: absolute; font-size: 30px; opacity: .10; line-height: 1; user-select: none;
  }
  .card .suit.tl { top: 6px; left: 10px; }
  .card .suit.tr { top: 6px; right: 10px; }
  .card .suit.bl { bottom: 6px; left: 10px; }
  .card .suit.br { bottom: 6px; right: 10px; }

  /* header band */
  .card-head {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 5mm;
  }
  .event {
    font-family: "Playfair Display", Georgia, serif;
    font-weight: 800; font-size: 15px; letter-spacing: .14em;
    color: #2a3142; text-transform: uppercase;
  }
  .serial {
    font-size: 11px; letter-spacing: .12em; color: #8a90a2;
    border: 1.5px solid #e2e4ee; border-radius: 999px; padding: 3px 11px;
    font-weight: 600;
  }

  /* BINGO letter row */
  .letters { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; margin-bottom: 6px; }
  .letters .lt {
    text-align: center; color: #fff; font-weight: 700;
    font-family: "Playfair Display", Georgia, serif;
    font-size: 34px; line-height: 1.35; border-radius: 12px;
    box-shadow: 0 3px 0 rgba(0,0,0,.12), inset 0 1px 0 rgba(255,255,255,.4);
  }
  .lt.b { background: linear-gradient(180deg,#f0567a,var(--b)); }
  .lt.i { background: linear-gradient(180deg,#5aa0ee,var(--i)); }
  .lt.n { background: linear-gradient(180deg,#3cc6a3,var(--n)); }
  .lt.g { background: linear-gradient(180deg,#f5c24a,var(--g)); }
  .lt.o { background: linear-gradient(180deg,#a274f6,var(--o)); }

  /* number grid */
  .grid {
    flex: 1; display: grid;
    grid-template-columns: repeat(5, 1fr);
    grid-template-rows: repeat(5, 1fr);
    grid-auto-flow: column; gap: 6px;
  }
  .cell {
    position: relative; display: grid; place-items: center;
    background: #fff; border-radius: 11px;
    border: 1.5px solid #e9ebf3;
    font-size: 40px; font-weight: 600; color: #232a3a;
    box-shadow: 0 1px 2px rgba(20,24,40,.05);
  }
  /* thin colour key per column, top edge */
  .cell::before {
    content: ""; position: absolute; top: 6px; left: 18%; right: 18%; height: 3px;
    border-radius: 3px; background: var(--c); opacity: .85;
  }
  .cell.b { --c: var(--b); } .cell.i { --c: var(--i); } .cell.n { --c: var(--n); }
  .cell.g { --c: var(--g); } .cell.o { --c: var(--o); }

  /* FREE centre */
  .cell.free { border: none; background: transparent; box-shadow: none; }
  .cell.free::before { display: none; }
  .free-badge {
    width: 86%; height: 86%; border-radius: 50%;
    display: grid; place-items: center; align-content: center;
    background: radial-gradient(circle at 35% 30%, #fff 0%, #ffe9a8 30%, #f4b400 75%, #d98f00 100%);
    box-shadow: 0 3px 10px rgba(217,143,0,.4), inset 0 2px 6px rgba(255,255,255,.6);
    color: #6a3d00;
  }
  .free-badge .star { font-size: 28px; line-height: .8; }
  .free-badge .word { font-size: 15px; font-weight: 700; letter-spacing: .12em; }

  /* footer */
  .card-foot {
    display: flex; align-items: center; justify-content: space-between;
    margin-top: 5mm; font-size: 11px; color: #9095a6; letter-spacing: .06em;
  }
  .card-foot .tag { font-style: italic; }
  .card-foot .dots { color: #d4d7e2; letter-spacing: 2px; }

  /* --------------------------- print rules ---------------------------- */
  @page { size: A4 portrait; margin: 0; }
  @media print {
    html, body { background: #fff; }
    .page {
      margin: 0; box-shadow: none;
      page-break-after: always; break-after: page;
    }
    .page:last-child { page-break-after: auto; break-after: auto; }
    .card { box-shadow: inset 0 0 0 6px #fff, inset 0 0 0 7px #ececf4; }
  }
</style>
"""

SUITS = ("♠", "♥", "♦", "♣")  # spade heart diamond club


def make_columns():
    """Return five columns of randomly-ordered numbers; N has a free centre."""
    cols = []
    for idx, (_letter, _accent, _tint) in enumerate(COLUMNS):
        lo = idx * 15 + 1
        pool = list(range(lo, lo + 15))
        k = 4 if idx == 2 else 5          # N column keeps 4 numbers + FREE
        cols.append(random.sample(pool, k))  # random order within the column
    return cols


def card_signature(cols):
    return "|".join(",".join(map(str, c)) for c in cols)


def render_cells(cols):
    """Emit 25 cells in column-major DOM order to match grid-auto-flow: column."""
    cls = ["b", "i", "n", "g", "o"]
    out = []
    for c in range(5):
        nums = cols[c]
        ni = 0
        for r in range(5):
            if c == 2 and r == 2:  # centre FREE space
                out.append(
                    '<div class="cell free">'
                    '<div class="free-badge"><div class="star">★</div>'
                    '<div class="word">FREE</div></div></div>'
                )
            else:
                out.append(f'<div class="cell {cls[c]}">{nums[ni]}</div>')
                ni += 1
    return "\n      ".join(out)


def render_card(cols, serial, total):
    suits = "".join(
        f'<span class="suit {pos}">{s}</span>'
        for pos, s in zip(("tl", "tr", "bl", "br"), SUITS)
    )
    letters = "".join(
        f'<div class="lt {l.lower()}">{l}</div>' for l, _, _ in COLUMNS
    )
    return f"""  <div class="card">
    {suits}
    <div class="card-head">
      <div class="event">{EVENT_NAME}</div>
      <div class="serial">No. {serial:0{len(str(total))}d}</div>
    </div>
    <div class="letters">{letters}</div>
    <div class="grid">
      {render_cells(cols)}
    </div>
    <div class="card-foot">
      <span class="tag">{TAGLINE}</span>
      <span class="dots">&bull; &bull; &bull;</span>
      <span>5 &times; 5</span>
    </div>
  </div>"""


def build_html(cards):
    pages = []
    for i in range(0, len(cards), 2):
        pair = cards[i:i + 2]
        body = pair[0]
        if len(pair) == 2:
            body += '\n  <hr class="cutline" />\n' + pair[1]
        pages.append(f'<div class="page">\n{body}\n</div>')
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        "<meta charset=\"UTF-8\" />\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n"
        f"<title>{EVENT_NAME} · Bingo Cards</title>\n"
        f"{STYLE}\n</head>\n<body>\n" + "\n".join(pages) + "\n</body>\n</html>\n"
    )


def main():
    num = int(sys.argv[1]) if len(sys.argv) > 1 else NUM_CARDS
    out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "bingo_cards.html"
    )

    if SEED is not None:
        random.seed(SEED)

    cards, seen = [], set()
    guard = 0
    while len(cards) < num:
        cols = make_columns()
        sig = card_signature(cols)
        guard += 1
        if sig in seen:
            if guard > num * 50:
                raise RuntimeError("Could not generate enough unique cards.")
            continue
        seen.add(sig)
        cards.append(render_card(cols, len(cards) + 1, num))

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(build_html(cards))

    print(f"Generated {num} unique cards -> {out_path}")
    print("Open it in a browser and Print to PDF (A4, margins: None) for 2 cards/page.")


if __name__ == "__main__":
    main()
