#set page(
  width: 12.8513in,
  height: 9.2500in,
  margin: 0pt,
  fill: rgb(35, 36, 36)
)

// Back Cover Image placed in the Back Panel area
#place(
  top + left,
  dx: 0.1250in,
  dy: 0.1250in,
  image("/root/journal/books/cover_assets/buku/sampulbelakang_english_amazon_selfhelp.jpeg", width: 6.0000in, height: 9.0000in, fit: "stretch")
)

// Front Cover Image placed in the Front Panel area
#place(
  top + left,
  dx: 6.7263in,
  dy: 0.1250in,
  image("/root/journal/books/cover_assets/buku/sampulbukubahsaenglish for sell amazon.jpeg", width: 6.0000in, height: 9.0000in, fit: "stretch")
)

// Spine Text (Rotated 90deg clockwise, standard US/Amazon KDP spine orientation)
#place(
  top + left,
  dx: 6.1250in,
  dy: 0in,
  box(
    width: 0.6013in,
    height: 9.2500in,
    fill: rgb(25, 26, 28),
    align(center + horizon)[
      #rotate(90deg, reflow: true)[
        #set text(font: "DejaVu Sans", fill: white)
        #box(width: 7.0500in)[
          #grid(
            columns: (auto, 1fr, auto),
            align: (left + horizon, center + horizon, right + horizon),
            [#text(size: 11.5pt, weight: "bold", fill: white)[MANIPULATIVE INTELLIGENCE]],
            [#text(size: 9pt, fill: rgb(235, 60, 60))[•]],
            [#text(size: 10.5pt, weight: "regular", fill: rgb(220, 222, 225))[ILHAM PRADANI]]
          )
        ]
      ]
    ]
  )
)
