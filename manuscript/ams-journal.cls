%% ams-journal.cls
%% LaTeX class for Applications of Modelling and Simulation (AMS) journal

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ams-journal}[2024/01/01 AMS Journal Class]

%% ---------------------------------------------------------------
%% Base class
%% ---------------------------------------------------------------
\LoadClass[10pt,a4paper,twoside]{article}

%% ---------------------------------------------------------------
%% Required packages
%% ---------------------------------------------------------------
\RequirePackage[T1]{fontenc}
\RequirePackage[utf8]{inputenc}
\RequirePackage{mathptmx}           % Times New Roman for text + math
\RequirePackage{helvet}             % Helvetica (for sans-serif fallback)
\RequirePackage{geometry}
\RequirePackage{graphicx}
\RequirePackage{amsmath,amssymb}
\RequirePackage{booktabs}
\RequirePackage{array}
\RequirePackage{caption}
\RequirePackage{fancyhdr}
\RequirePackage{setspace}
\RequirePackage{parskip}
%\RequirePackage{indentfirst}
\RequirePackage{titlesec}
\RequirePackage{xcolor}
\RequirePackage{url}
\RequirePackage{hyperref}
\RequirePackage{cite}
\RequirePackage{enumitem}
\RequirePackage{microtype}
\RequirePackage{lastpage}
\RequirePackage{etoolbox}
\RequirePackage{lineno}

\RequirePackage{FiraSans}
\RequirePackage{sourcesanspro}
\RequirePackage{raleway}
\RequirePackage{montserrat}
\RequirePackage{noto-sans}
\RequirePackage{comment}


% Author supersripts control block %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\renewcommand{\textsuperscript}[1]{%
  {\fontsize{7}{0}\selectfont\raisebox{1.2ex}{#1}} % The first number is the font size for the author superscripts
  \unskip
}                                                  % The last nuber can be adjusted to change how high the author superscripts are  
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%% ---------------------------------------------------------------
%% Page geometry  (A4)
%% top/bottom = 17.8 mm, left/right = 16.5 mm
%% header = 7.6 mm from edge, footer = 5.1 mm from edge
%% ---------------------------------------------------------------
\geometry{
  a4paper,
  top      = 17.0mm,
  bottom   = 23.5mm,
  left     = 16.5mm,
  right    = 16.5mm,
  headsep  = 2.2mm,   % top - headheight - (header from edge)
  headheight = 10pt,
  footskip = 12.5mm
}

%% ---------------------------------------------------------------
%% Paragraph formatting
%% ---------------------------------------------------------------
\setlength{\parindent}{4mm}
\setlength{\parskip}{0pt}

%% ---------------------------------------------------------------
%% Title block commands
%% ---------------------------------------------------------------
\renewcommand{\@maketitle}{%
  \newpage
  \null
  % Title
  \vspace{60pt} % change this value if spacing between title and header needs to be adjusted
  {\centering\fontsize{22}{26}\selectfont\@title\par}%
  \vspace{12pt} % spacing between title and names of authors
  % Authors
  {\centering\fontsize{11}{12}\selectfont\renderauthors\par}%
  \vspace{13pt}  % spacing between names of authors and affliations
  % Affiliations
  \@ifundefined{@affiliation}{}{%
    {\centering\fontsize{10}{12}\selectfont\@affiliation\par}%
    \vspace{5pt} % spacing between affliations and corresponding author text
  }%
  % Corresponding author
  \@ifundefined{@corresponding}{}{%
    {\raggedright\fontsize{10}{12}\selectfont\textsuperscript{*}Corresponding author: \@corresponding\par}%
    \vspace{6pt} % spacing between corresponding author text and manuscript processing dates
  }%
  % Dates
  \@ifundefined{@dates}{}{%
    {\raggedright\fontsize{10}{12}\itshape\selectfont\@dates\par}%
    \vspace{0pt} % spacing between manuscript processing dates and Copyright text
  }%
  % Copyright
  \@ifundefined{@copyrightyear}{}{%
    {\raggedright\fontsize{10}{13}\selectfont Copyright \textcopyright{} \@copyrightyear{} The Authors.\par}%
  }%
  \vspace{4pt}%
}

%% Commands for metadata
\newcommand{\affiliation}[1]{\gdef\@affiliation{#1}}

%% ---------------------------------------------------------------
%% Multi-author list with automatic comma and "and" before last author
%% Usage in main.tex  (replaces \author{...}):
%%   \addauthor{First A. Author\textsuperscript{1*}}
%%   \addauthor{Second B. Author\textsuperscript{1,2}}
%%   \addauthor{Third C. Author\textsuperscript{2}}
%% ---------------------------------------------------------------
\newcounter{ams@numauthors}          % total count of \addauthor calls
\newcounter{ams@curauthor}           % loop counter when rendering

\newcommand{\addauthor}[1]{%
  \stepcounter{ams@numauthors}%
  \expandafter\gdef\csname ams@author@\theams@numauthors\endcsname{#1}%
}

%% \renderauthors builds:  A, B and C   or   A and B   or   A
\newcommand{\renderauthors}{%
  \setcounter{ams@curauthor}{0}%
  \@whilenum\value{ams@curauthor}<\value{ams@numauthors}\do{%
    \stepcounter{ams@curauthor}%
    \ifnum\value{ams@curauthor}>1
      \ifnum\value{ams@curauthor}=\value{ams@numauthors}
        \ and %                      % "and" before last author
      \else
        ,\ %                         % comma between middle authors
      \fi
    \fi
    \csname ams@author@\theams@curauthor\endcsname
  }%
}
\newcommand{\corresponding}[1]{\gdef\@corresponding{#1}}
\newcommand{\dates}[1]{\gdef\@dates{#1}}
\newcommand{\copyrightyear}[1]{\gdef\@copyrightyear{#1}}
\newcommand{\volume}[1]{\gdef\@volume{#1}}
\newcommand{\pubyear}[1]{\gdef\@pubyear{#1}}
\newcommand{\pages}[1]{\gdef\@pages{#1}}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% EDITOR FIELDs %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\newcommand{\firstauthor}[1]{\gdef\@firstauthor{#1}}
\gdef\@firstauthor{}     % 1.  @@@@@@@@@@ EDITOR FIELD @@@@@ Provide first author information in BLOCK letters here. 
                         %     For example, the template has First A. Author as first author's name. 
                         %     Put "F. A. AUTHOR ET AL." since we have three authors in the template

\gdef\@volume{XX}         % 2.  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ to be inserted by the editor (e.g., 7)
\gdef\@pubyear{20XX}     % 3.  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ to be inserted by the editor (e.g., 2026)
\gdef\@pages{XXX--XXX}   % 4.  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ to be inserted by the editor (e.g.,101-118)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%% ---------------------------------------------------------------
%% Abstract and keywords environment
%% ---------------------------------------------------------------
\renewenvironment{abstract}{%
  \vspace{6pt}%
  \noindent\rule{\linewidth}{0.4pt}\par
  \vspace{-1pt} % top rule line spacing from abstract text
  \noindent\fontsize{10}{12}\selectfont
  \textbf{Abstract: }%
  \ignorespaces
}{%
  \par
  \vspace{2pt}%
  \vspace{6pt}%
}

\newcommand{\keywords}[1]{%
  %\noindent\rule{\linewidth}{0.4pt}%
  \par\vspace{4pt}%
  \noindent\fontsize{10}{12}\selectfont
  \textnormal{Keywords: }#1\par
  \vspace{-8pt} % bottom rule line spacing from keyword text
  \noindent\rule{\linewidth}{0.4pt}%
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  \vspace{-12pt} % spacing between keywords and the first section (INTRODUCTION) %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
}

%% ---------------------------------------------------------------
%% Section headings
%%   Section:    bold, uppercase, 10pt, numbered, no extra space
%%   Subsection: bold, 10pt
%%   Subsubsection: italic, 10pt
%% ---------------------------------------------------------------
\titleformat{\section}
  {\normalfont\fontsize{10}{15}\bfseries}
  {\thesection.}
  {0.5em}
  {\MakeUppercase}

\titleformat{\subsection}
  {\normalfont\fontsize{10}{15}\bfseries}
  {\thesubsection}
  {0.5em}
  {}

\titleformat{\subsubsection}
  {\normalfont\fontsize{10}{20}\itshape}
  {\thesubsubsection}
  {0.5em}
  {}

\titlespacing*{\section}{0pt}{10pt plus 2pt minus 2pt}{4pt}
\titlespacing*{\subsection}{0pt}{8pt plus 2pt minus 2pt}{2pt}
\titlespacing*{\subsubsection}{0pt}{6pt plus 2pt minus 2pt}{2pt}

%% ---------------------------------------------------------------
%% Captions
\captionsetup{
  font      = {normalsize},
  labelsep  = period,
  justification = centering,
  singlelinecheck = false
}
\captionsetup[figure]{position=below}
\captionsetup[table]{position=above}

%%---------------------------------------------------------------
%% Header / Footer  (fancyhdr)
%% ---------------------------------------------------------------

\fancypagestyle{firstpage}{%
  \fancyhf{}%
  %% -------------- HEADER -------------------
  \fancyhead[L]{%
    \begin{minipage}[b]{0.30\linewidth}%
      \raggedright
      \includegraphics[height=15mm]{template_images/arqii_logo}\\[-7pt]%
      {\fontfamily{ppl}\fontsize{8}{9}\selectfont \textbf{http://arqiipubl.com/ams}}%
    \end{minipage}%
  }%
  \fancyhead[R]{%
    \begin{minipage}[b]{0.66\linewidth}%
      \raggedleft
        \includegraphics[height=12.5mm]{template_images/Journal_name.png}\\%
      {\fontfamily{ppl}\fontsize{8}{9}\selectfont
        \textbf{eISSN 2600-8084}\hspace{152pt} \textbf{VOL \@volume, \@pubyear, \@pages}}%
    \end{minipage}%
  }%
  \renewcommand{\headrulewidth}{2pt}%

  
  %% ----------- FOOTER -------------------
  \fancyfoot[L]{%
    \begin{minipage}[t]{0.80\linewidth}%
      \vspace{-8pt}% top alignment of creative common text
      {\fontsize{9}{2.5}\selectfont
        This article is distributed under a Creative Commons Attribution 4.0 License that permits any use, reproduction\\[-2pt]
         and distribution of the work without further permission provided that the original work is properly cited.}%
    \end{minipage}%
  }%
  \fancyfoot[R]{%
    \begin{minipage}[t]{0.2\linewidth}%
      \raggedleft\vspace{-12pt}% top alignment of creative common logo
      \includegraphics[height=6.5mm]{template_images/cc_badge}\hspace{12pt}\raisebox{3.5mm}{\fontsize{9}{6}\selectfont\thepage}
    \end{minipage}%
  }%
  \renewcommand{\footrulewidth}{0.4pt}%
}


%% ---- Subsequent pages -----------------------------------------
\fancypagestyle{plain}{%
  \fancyhf{}%
  \renewcommand{\headrulewidth}{0.4pt}%
  \fancyhead[C]{%
    {\fontfamily{ppl}\fontsize{8}{10}\selectfont
     \@firstauthor\ifx\@firstauthor\empty\else,\ \fi
     APPLICATIONS OF MODELLING AND SIMULATION,
     VOL \@volume, \@pubyear, \@pages}%
  }%
  \renewcommand{\footrulewidth}{0pt}%
  \fancyfoot[R]{\fontsize{9}{11}\selectfont\thepage}%
}



\pagestyle{plain}

%% Apply firstpage style on page 1 (hook into \maketitle)
\let\ams@oldmaketitle\maketitle
\renewcommand{\maketitle}{%
  \ams@oldmaketitle
  \thispagestyle{firstpage}%
}
\AtBeginDocument{\thispagestyle{firstpage}}

%% ---------------------------------------------------------------
%% References  (numeric, square brackets)
%% ---------------------------------------------------------------
\renewcommand{\refname}{\normalfont\fontsize{10}{12}\bfseries\MakeUppercase{References}}

%% ---------------------------------------------------------------
%% Hyperref setup
%% ---------------------------------------------------------------
\hypersetup{
  colorlinks = true,
  linkcolor  =blue,
  citecolor  = blue,
  urlcolor   = blue,
  pdfborder  = {0 0 0}
}


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% EDITOR FIELDs %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\dates{
  Submitted DD MM YYYY;             % 5.  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ to be inserted by the editor (5 March 2026)
  Revised DD MM YYYY;               % 6.  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ to be inserted by the editor (27 May 2026)
  Accepted DD MM YYYY;              % 7.  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ to be inserted by the editor (15 June 2026)
  Available online DD MM YYYY.      % 8.  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ to be inserted by the editor (23 June 2026)
}

\copyrightyear{20XX}                 % 9.  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ to be edited by the editor 
\setcounter{page}{1}                 % 10. @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ to be edited by the editor (e.g., 101)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\urlstyle{same}

\endinput
