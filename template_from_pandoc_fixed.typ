#let horizontalrule = line(start: (25%,0%), end: (75%,0%))

#show terms: it => {
  it.children
    .map(child => [
      #strong[#child.term]
      #block(inset: (left: 1.5em, top: -0.4em))[#child.description]
      ])
    .join()
}

#set table(
  inset: 6pt,
  stroke: none
)

#show figure.where(
  kind: table
): set figure.caption(position: top)

#show figure.where(
  kind: image
): set figure.caption(position: bottom)

#let content-to-string(content) = {
  if content.has("text") {
    content.text
  } else if content.has("children") {
    content.children.map(content-to-string).join("")
  } else if content.has("body") {
    content-to-string(content.body)
  } else if content == [ ] {
    " "
  }
}
#let conf(
  title: none,
  subtitle: none,
  authors: (),
  keywords: (),
  date: none,
  abstract: none,
  cols: 1,
  margin: (x: 1.25in, y: 1.25in),
  paper: "us-letter",
  lang: "en",
  region: "US",
  font: ("Liberation Serif", "Times New Roman"),
  fontsize: 11pt,
  sectionnumbering: none,
  pagenumbering: "1",
  doc,
) = {
  set document(
    title: title,
    author: authors.map(author => content-to-string(author.name)),
    keywords: keywords,
  )
  set page(
    paper: paper,
    margin: margin,
    numbering: pagenumbering,
    columns: cols,
    )
  set par(justify: true)
  set text(lang: lang,
           region: region,
           font: ("Liberation Serif", "Times New Roman"),
           size: fontsize)
  set heading(numbering: sectionnumbering)

  place(top, float: true, scope: "parent", clearance: 4mm)[
  #if title != none {
    align(center)[#block(inset: 2em)[
      #text(weight: "bold", size: 1.5em)[#title]
      #(if subtitle != none {
        parbreak()
        text(weight: "bold", size: 1.25em)[#subtitle]
      })
    ]]
  }

  #if authors != none and authors != [] {
    let count = authors.len()
    let ncols = calc.min(count, 3)
    grid(
      columns: (1fr,) * ncols,
      row-gutter: 1.5em,
      ..authors.map(author =>
          align(center)[
            #author.name \
            #author.affiliation \
            #author.email
          ]
      )
    )
  }

  #if date != none {
    align(center)[#block(inset: 1em)[
      #date
    ]]
  }

  #if abstract != none {
    block(inset: 2em)[
    #text(weight: "semibold")[Abstract] #h(1em) #abstract
    ]
  }
  ]

  doc
}
#show: doc => conf(
  pagenumbering: "1",
  cols: 1,
  doc,
)


#strong[Article Title (Palatino Linotype, Font Size 16 point, bold,
centered, max 15 words)]

#emph[#strong[(one blank single space line, 16 pt)];]

First Author#super[1.2 \*];, Second Author#super[1];, Third
Author#super[2] (12 pt)

\1. Department, Faculty, University, Country (10 pt)

\2. Research Group, Institution, Country (10 pt)

\*corresponding author e-mail : name\@ institution address.com (10 pt)

#figure(
  align(center)[#table(
    columns: (34.58%, 65.42%),
    align: (auto,auto,),
    table.header(table.cell(align: left)[Article
      Info], table.cell(align: left, rowspan: 3)[Abstract

      Written in English. Using type abstract one paragraph
      unstructured, A4 11 point, single spacing, right-left flat, the
      number of words does not exceed 200 words, there are no quotes and
      abbreviations/acronyms. The abstract must contain an introduction
      or the problem under study including the purpose of the study if
      possible, make it in one sentence. Research design, the method of
      taking and sample size, methods and data collection, and data
      analysis. Findings. (OR / RR, CI or theme in qualitative
      research). Write one or two sentences to discuss the results and
      conclusions. The recommendations and implications of the research
      results are clearly written.

      ],
      table.cell(align: left)[#emph[Keywords:]

      Culture;

      Genre;

      Translation

      ],
      table.cell(align: left)[],),
    table.hline(),
  )]
  , kind: table
  )

#strong[Introduction (12 pt., bold, sentence case)]

The script is written in Palatino Linotype size 12, single spacing, flat
left and right, single-sided pages, made in one column with A4 paper
(210 mm x 297 mm) with a margin of 2,7 cm, bottom 2.5 cm, left and right
respectively 2 cm. Manuscripts including graphic content and tables must
consist of (4000--6000 words), preferably an even number of pages. If it
exceeds the specified length, it is recommended to divide it into two
separate texts. Grammar must be correct.

Abstract is written in English followed by Indonesian. Using type
abstract one paragraph unstructured, letters 10 pt., single spacing,
right-left flat, the number of words does not exceed 200 words. There
are no quotes and abbreviations/acronyms. The abstract must contain an
introduction, or the problem studied including the purpose of the study;
if possible, make it in one sentence. Research design must contain
sampling techniques, methods and data collection, and data analysis. As
for main findings (OR / RR, CI or theme in qualitative research), write
one or two sentences to discuss the results and conclusions. The
recommendations and implications of the research results are clearly
written.

Abstract is written in English followed by Indonesian. Using type
abstract one paragraph unstructured, letters 10 pt., single spacing,
right-left flat, the number of words does not exceed 200 words. There
are no quotes and abbreviations/acronyms. The abstract must contain an
introduction, or the problem studied including the purpose of the study;
if possible, make it in one sentence. Research design must contain
sampling techniques, methods and data collection, and data analysis. As
for main findings (OR / RR, CI or theme in qualitative research), write
one or two sentences to discuss the results and conclusions. The
recommendations and implications of the research results are clearly
written.

The script is written in New Times Roman size 12, single spacing, flat
left and right, single-sided pages, made in one column with A4 paper
(210 mm x 297 mm) with a margin of 2,7 cm, bottom 2.5 cm, left and right
respectively 2 cm. Manuscripts including graphic content and tables must
consist of (4000--6000 words), preferably an even number of pages. If it
exceeds the specified length, it is recommended to divide it into two
separate texts. Grammar must be correct.

Titles must contain the main keywords and do not use abbreviations, with
a number of approximately 20 words. The author needs to write a short
title written as a header page on each journal page. The author should
not only write words.

The use of abbreviations is allowed but must be written in a full and
complete version as mentioned for the first time and must be written
between parentheses. Foreign terms/words or regional words must be in
italics. Notation must be concise and clear and written according to the
standard writing style. Symbols/signs must be clear and distinguishable,
such as the use of numbers 1 and letter l (also numbers 0 and letter O).
Avoid using parentheses to clarify or explain definitions. The
composition of the text includes Introduction, Methods, Results and
Discussion, Conclusions and References (if any) written afterwards, not
numbered.

This text uses the style of the American Psychological Association (APA)
manual as a reference quote. As using the APA format, follow the method
of quotation in the text written by the author. This means that the
author's last name and year of publication for the source must appear in
the text, for example, (Jones, 1998) and complete references will appear
in the reference list at the end of the text. Quotes can be placed at
the beginning of a sentence, for example, Johnson (2005) states that ...
or the source is placed at the end of the sentence for an example ...
(Mardoni, 2004).

It is recommended that the author uses the #strong[manager references]
(Mendeley, endnote, etc.)

The introduction contains justifications about the importance of the
research conducted. The novelty generated from this study comparing the
results of previous studies or existing umbrella knowledge needs to be
clearly displayed. Complete with the main reference used. State in one
research question or research problem that needs to be answered by all
research activities. Show the method used and the purpose or research
hypothesis. The introduction does not exceed 1000 words.

#strong[Table 1.] Characteristics of Research Subjects

#figure(
  align(center)[#table(
    columns: (45.47%, 21.73%, 32.8%),
    align: (auto,auto,auto,),
    table.header([#strong[Characteristics];], table.cell(align: center)[#strong[N];], table.cell(align: center)[#strong[Percentage
      (%)];],
      [Age], table.cell(align: center)[0], table.cell(align: center)[0.00],
      [Type
      Gender], table.cell(align: center)[0], table.cell(align: center)[0.00],
      [Number of
      children], table.cell(align: center)[0], table.cell(align: center)[0.00],),
    table.hline(),
  )]
  , kind: table
  )

(one single-spaced line, 10 pt.)

Source: ……………….

Images are placed symmetrically in columns in one paragraph space.
Images are placed in the top or bottom position of each page and are not
flanked by sentences. If the image size exceeds the column width, the
image can be placed in one column format. Images are placed immediately
after the description in the manuscript. Images are numbered and sorted
by Arabic numerals. Information is placed under the image and in one
single space of the image. The description is written using a 10pt font
size, bold letters, uppercase letters at the beginning of the word, and
placed as in the example. The distance between the description and
paragraph is two single spaces.

Images that have been published by other authors must obtain written
permission from the author and publisher. Include good quality printed
images on one full page or scan with good resolution in the format
{filename} .jpeg or {filename}. have a fight. When the image is in a
photo format, include the original photo. The image will be printed in
black and white unless it needs to be displayed in color. The author
will incur additional costs for printing colors if more than one page.
Fonts used in images or graphics must be owned in general by every word
processor and the operating system such as Symbol, Times New Roman, and
Arial with a size of not less than 9 pt. Image files originating from
applications such as Corel Draw, Adobe Illustrator, and Aldus Freehand
can provide better results and can be reduced without changing the
resolution.

The following are examples of images included in the manuscript.

#box(image("./media/image3.png", height: 2.49798in, width: 3.91598in))

#strong[Figure 1.] Theory of planned behavior (Ajzen, 1991)

(Capital letters in the beginning of the word, bold, 10 pt.)

For qualitative studies, findings are usually written in the form of
quotations from research informants. The table format is rarely used
except to describe the characteristics of participants or recapitulate
themes or categories. If the quote is no more than 40 words, then use
quotation marks (“”) at the beginning and at the end of the sentence and
include informants who give statements without the need to make separate
paragraphs. Ellipsis (...) is only used to change words that are not
displayed, not stop/pause.

#strong[Research Method]

Methods contain the design, size, criteria, and method of sampling,
instruments used and collection procedures, processing, and data
analysis. When using a questionnaire as an instrument, explain the
contents briefly and to measure which variables. The validity and
reliability of the instrument must also be explained. In experimental
research or interventions, it is necessary to explain the intervention
procedure or treatment provided. In this section, it must explain how
research ethics approval is obtained and the protection of the rights of
the respondents imposed. Data analysis using a computer program does not
necessarily mention details of the software if it is not original
software. For qualitative research, this section needs to explain how
research safeguards the validity of the data obtained. The method
section is written briefly in two to three paragraphs with a maximum of
600 words.

#strong[Results and Discussions]

The findings are sorted by research objectives or research hypotheses.
The results do not display the same data in two forms, namely
tables/images/graphics and narration. There is no quote in the results
section.

This section explains the results of the study. It must be presented
clearly and concisely. The author must explore the novelty or
contribution of the work to economic literature. Clearly show the
results of the analysis and the discussion by using the relevant and
updating references.

Tables only use 3 (three) rows (do not use column lines), row headings,
and end tables (see examples). Tables are written with Times New Roman
size of 10 pt. and placed in one space under the title table. The table
title is written in 9 pt. bold, uppercase letters at the beginning of
the word and placed on a table in the format shown in the example that
does not use column lines. Numbering tables use Arabic numerals. The
distance between a table and a paragraph is a single space. The table is
placed immediately after its appointment in the manuscript. The table
frame uses a line size of 1 pt. If the table has many columns, it can
use one column format in half or full pages. If the title in each table
column is long and complicated, the column is numbered, and the
description is given at the bottom of the table. The table is placed at
the top or bottom of each page and is not flanked by sentences. Avoid
interrupting table by page.

#strong[Conclusions]

A section is written in narrative. Conclusions are answers to hypotheses
that lead to the main purpose of the research. In this section, it is
not permissible to cite the work of other authors and new information or
terms that did not previously exist. Further information can be written
in this section.

#strong[References]

References are written in Times New Roman font size 12-point, line space
at least 15 pt. for the distance between references included. References
use a hanging pattern, which is the second row protrudes by 0.25\".
References only contain articles that have been published and are
selected that are most relevant to the text. The reference format
follows the style of the\" name-year \"quote (reference APA 6#super[th]
edition). All sources in the reference must be referenced in the text
and what is in the text must be in this reference. The author must write
the name of the author's last name and the year of publication in the
use of parentheses, for example (Potter & Perry, 2006) or Potter and
Perry (2006) Write the name of the first author and “et al.”, if there
are more than six authors, for example (Potter, et al., 2006) or Potter
et al. (2006).

#strong[Journal]

Author, AA, Author, BB, & Author, CC (year). Article title: Sub-title.
#emph[Journal Title];, #emph[volume];(issue number), page numbers

#quote(block: true)[
Altman, EI, & Kuehne, BI, (2016) Credit markets and bubbles: Is the
credit cycle over Economics and Business Review, #emph[16];(3), 20-31.
Doi: 10.18559 / ebr .2016.3.3
]

Huda, N., Rini, N., Mardoni, Y., Hudori, K., & Anggraini, D. (2017).
lems, Solutions and Strategies Priority for Waqf in Indonesia. Journal
of Economic Cooperation & Development, #emph[38];(1), 29.

#strong[Proceedings of the conference]

Schnase, JL, & Cunnius, EL (Eds.). (1995). Proceedings from CSCL \'95:
#emph[The First] #emph[International Conference on Computer Support for
Collaborative Learning];. Mahwah, NJ: Erlbaum.

#strong[Book]

Author, AA (Year). #emph[Source title: Capital letter at] #emph[the
beginning of the subtitle];. Location / City: Publisher.

Borner, S., Brunetti, A., & Weder, B. (1995). #emph[Political
credibility and economic development.] New York, NY: Macmillan.

Chapter in the

Author, AA (Year) book. Chapter title#emph[: Capital] #emph[letter at
the beginning of the subtitle.] In Initial, Surname (Author\'s name/book
editor) (eds). #emph[Book title];. Location / City: Publisher.

Daszkiewicz, N., & Olczyk, M. (2014). Competitiveness of the Visegrad
countries - Paths for competitiveness growth. In D, Kiendl-Wendner, K.
Wach (Eds.), International competitiveness in Visegrad countries: Macro
and micro perspectives (pp. 33-52). Graz: Fachhochschule Joanneum.

Book translation of

Ganong, WF (2008). #emph[Medical Physiology (];Ed 22nd). (Peter A.,
trans). New York: McGraw Hill Medical. (Original book published 2005).

#strong[Thesis / Dissertation]

If available in the #emph[database]

Gilliland, AL (#emph[2010). A grounded theory model] #emph[of effective
labor support by doulas] (Doctoral Dissertation). Obtained from
#emph[ProQuest] #emph[Dissertations and Theses. (UMI No 3437269)]

If not published

Last-name, AA (year). Dissertation/thesis title#emph[.] (Unpublished
doctoral dissertation/master thesis). Institution Name, Location.

Considine, M. (1986). #emph[Australian insurance] #emph[politics in the
1970s: Two case studies];. (Unpublished doctoral dissertation). The
University of Melbourne, Melbourne, Australia.

#strong[Database Article]

Author, A. A., Author, B. B., & Author, C. C. (Year pub). Title of the
article. #emph[Title of Journal];, Volume (Issue), pp-pp. doi:
xx.xxxxxxxxx \[OR\] Retrieved from URL of publication\'s home page

Borman, WC, Hanson, MA, Oppler, SH, Pulakos, ED, & White, LA (1993).
Role of early

supervisory experience in supervisor performance. #emph[Journal of
Applied Psychology,]

#emph[78];(8), 443-449. Obtained from
#underline[http:\/\/www.eric.com/jdlsiejls/] supervisor / early937d%

Database article with DOI (Digital Object Identifier)

Brownlie, D. (2007). Toward effective poster presentations: An annotated
bibliography. #emph[European Journal of Marketing, 41];(11/12),
1245-1283. doi: 10.1108 / 03090560710821161

#strong[Other online sources are]

Author, AA (year). Title of source. Retrieved from URL of publication\'s
home page

Article from website

Exploring Linguistics. (1999, August 9). Retrieved from
#underline[http:\/\/logos.uoregon.edu/explore/];orthography /
chinese.html \# tsang

Electronic article

Becker, E. (2001, August 27). Prairie Farmers reap conservation's
rewards. #emph[The New York] #emph[Times];, pp. 12-90. Retrieved from
http:\/\/www.nytimes.com

#quote(block: true)[
(One blank single space line, 12 pt.)
]
