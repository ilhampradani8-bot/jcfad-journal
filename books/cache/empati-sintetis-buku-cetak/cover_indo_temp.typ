#set page(
  width: 12.9680in,
  height: 9.2500in,
  margin: 0pt,
  fill: rgb(35, 36, 36)
)

#place(
  top + left,
  dx: 0.1250in,
  dy: 0.1250in,
  image("/root/journal/books/cover_assets/buku/sampulbelakang_indo_googlebooks_selfhelp.jpeg", width: 6.0000in, height: 9.0000in, fit: "stretch")
)

#place(
  top + left,
  dx: 6.8434in,
  dy: 0.1250in,
  image("/root/journal/books/cover_assets/buku/sampulbukubahsa indo for sell tulisan kecerdasan manipulatif.jpeg", width: 6.0000in, height: 9.0000in, fit: "stretch")
)

#place(
  top + left,
  dx: 6.1250in,
  dy: 0in,
  box(
    width: 0.7184in,
    height: 9.2500in,
    fill: rgb(25, 26, 28),
    align(center + horizon)[
      #rotate(90deg, reflow: true)[
        #set text(font: "DejaVu Sans", fill: white)
        #box(width: 7.0500in)[
          #grid(
            columns: (auto, 1fr, auto),
            align: (left + horizon, center + horizon, right + horizon),
            [#text(size: 11pt, weight: "bold", fill: white)[KECERDASAN MANIPULATIF]],
            [#text(size: 8.5pt, fill: rgb(235, 60, 60))[•]],
            [#text(size: 10pt, weight: "regular", fill: rgb(220, 222, 225))[ILHAM PRADANI]]
          )
        ]
      ]
    ]
  )
)
