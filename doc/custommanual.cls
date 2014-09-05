%
% sphinxmanual.cls for Sphinx (http://sphinx-doc.org/)
%
\usepackage[utf8]{inputenc}

\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{custommanual}[2009/06/02 Document class (Sphinx manual)]

% chapters starting at odd pages (overridden by 'openany' document option)
\PassOptionsToClass{openright}{\sphinxdocclass}

% 'oneside' option overriding the 'twoside' default
\newif\if@oneside
\DeclareOption{oneside}{\@onesidetrue}
% Pass remaining document options to the parent class.
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{\sphinxdocclass}}
\ProcessOptions\relax

% Defaults two-side document
\if@oneside
% nothing to do (oneside is the default)
\else
\PassOptionsToClass{twoside}{\sphinxdocclass}
\fi

\LoadClass{\sphinxdocclass}

% Set some sane defaults for section numbering depth and TOC depth.  You can
% reset these counters in your preamble.
%
\setcounter{secnumdepth}{2}
\setcounter{tocdepth}{1}

% Change the title page to look a bit better, and fit in with the fncychap
% ``Bjarne'' style a bit better.
%
\renewcommand{\maketitle}{%
  \begin{titlepage}%
    \let\footnotesize\small
    \let\footnoterule\relax
    \ifsphinxpdfoutput
      \begingroup
      % These \defs are required to deal with multi-line authors; it
      % changes \\ to ', ' (comma-space), making it pass muster for
      % generating document info in the PDF file.
      \def\\{, }
      \def\and{and }
      \pdfinfo{
        /Author (\@author)
        /Title (\@title)
      }
      \endgroup
    \fi

    \vspace*{\fill}
    \begin{center}

      \begin{varwidth}{14cm}
        \centering
        \Huge \@title
      \end{varwidth}

      \vspace{1cm}
      {\Large\sc Anexo III}

      {\Large Manual de usuario}

      \includegraphics[width=13cm]{Logo_Usal_Hor_2012.pdf}

      \vspace{0.5cm}
      {\centering \Large Septiembre de 2014} 
      \vspace{2cm}

      \begin{varwidth}{16cm}
        \centering

        \large

        {\bf Autor}\par
        \@author

        \vspace{0.5cm}
        {\bf Tutora}\par
        Ángeles Mª Moreno Montero

      \end{varwidth}
    \end{center}
    \vspace*{\fill}

  \end{titlepage}%
  \cleardoublepage%
  \setcounter{footnote}{0}%
  \let\thanks\relax\let\maketitle\relax
  %\gdef\@thanks{}\gdef\@author{}\gdef\@title{}
}

% Catch the end of the {abstract} environment, but here make sure the abstract
% is followed by a blank page if the 'openright' option is used.
%
\let\py@OldEndAbstract=\endabstract
\renewcommand{\endabstract}{
  \if@openright
    \ifodd\value{page}
      \typeout{Adding blank page after the abstract.}
      \vfil\pagebreak
    \fi
  \fi
  \py@OldEndAbstract
}

% This wraps the \tableofcontents macro with all the magic to get the spacing
% right and have the right number of pages if the 'openright' option has been
% used.  This eliminates a fair amount of crud in the individual document files.
%
\let\py@OldTableofcontents=\tableofcontents
\renewcommand{\tableofcontents}{%
  \definecolor{dark-gray}{gray}{0.15}
  \hypersetup{linkcolor=dark-gray}
  \pagenumbering{roman}%
  \setcounter{page}{1}%
  \pagebreak%
  \pagestyle{plain}%
  {%
    \parskip = 0mm%
    \py@OldTableofcontents%
    \if@openright%
      \ifodd\value{page}%
        \typeout{Adding blank page after the table of contents.}%
        \pagebreak\hspace{0pt}%
      \fi%
    \fi%
    \cleardoublepage%
  }%
  \pagenumbering{arabic}%
  \@ifundefined{fancyhf}{}{\pagestyle{normal}}%
}
\pagenumbering{alph}

% This is needed to get the width of the section # area wide enough in the
% library reference.  Doing it here keeps it the same for all the manuals.
%
\renewcommand*\l@section{\@dottedtocline{1}{1.5em}{2.6em}}
\renewcommand*\l@subsection{\@dottedtocline{2}{4.1em}{3.5em}}

% Fix the bibliography environment to add an entry to the Table of
% Contents.
% For a report document class this environment is a chapter.
\let\py@OldThebibliography=\thebibliography
\renewcommand{\thebibliography}[1]{
  \cleardoublepage
  \phantomsection
  \py@OldThebibliography{1}
  \addcontentsline{toc}{chapter}{\bibname}
}

% Same for the indices.
% The memoir class already does this, so we don't duplicate it in that case.
%
\@ifclassloaded{memoir}{}{
  \let\py@OldTheindex=\theindex
  \renewcommand{\theindex}{
    \cleardoublepage
    \phantomsection
    \py@OldTheindex
    \addcontentsline{toc}{chapter}{\indexname}
  }
}
