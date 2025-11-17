%*************************************
% UQ Thesis Formatting Style Class
%*************************************
% uqthesis.cls

% This file defines the formatting style for your thesis in accordance with the Thesis Format Requirements (See Section 7 of UQ Procedure 4.60.08 Higher Degree by Research Examination)
% for Masters and PhD theses.

%*************************************
% Class structure: identification part
%*************************************

\ProvidesClass{uqthesis}[2018/06/26 version 1.01 UQ PhD and Masters thesis style]
\NeedsTeXFormat{LaTeX2e}[2016/05/16]

%Load the memoir class.
\LoadClass[12pt, a4paper]{memoir}

%*************************************
% Load packages
%*************************************
\RequirePackage{mathptmx} 							
%Set the font to Times New Roman. This package also alters the math-mode font to TNR.

\RequirePackage{graphicx}								
%Use pdfLaTeX.

\RequirePackage{booktabs, longtable} 		
%These allow tables to split over pages. Very useful in theses!

\RequirePackage{url} 									
%Typeset urls properly.

\RequirePackage{hyperref}							
%Hyperlink your pdf output.

\RequirePackage{geometry}								
%This allows us to set the margins correctly.

\RequirePackage{memhfixc}							
	%Need this to make sure the layout is correct.
	
\RequirePackage{amsmath,amssymb,amsthm} 
%Useful maths packages.

\RequirePackage{setspace}								
%Used to set the appropriate linespacing.

\RequirePackage{uqtitle}								
%Get the title page right.

\RequirePackage{comment}								
%Use this to enable easy inclusion/exclusion of instructions (at request of grad school).

%*************************************
% Turn off instructional comments
%*************************************
%This section of code allows the template user to turn off the instructional comments with a single option.
%Adapted from https://tex.stackexchange.com/questions/135248/if-not-declareoption
	\newif\ifmycomments@comments
	\DeclareOption{instructions}{\mycomments@commentstrue}
	\DeclareOption{final}{\mycomments@commentsfalse}

	\ExecuteOptions{draft} % default is to have no comments.
	\excludecomment{instructional}

	\ProcessOptions\relax

	\ifmycomments@comments
		\includecomment{instructional} %include comments if true
	\fi

%*************************************
% Set page and heading styles
%*************************************
% ********* Set page layout **********
\setlrmarginsandblock{20mm}{20mm}{*}
\setulmarginsandblock{20mm}{20mm}{*}

\setheadfoot{15mm}{\baselineskip}
\setheaderspaces{*}{\baselineskip}{*}

\def\baselinestretch{1.1}

%Make sure that TeX sorts out the geometry correctly.
\checkandfixthelayout

% ********* Chapter and section style **********
\makechapterstyle{mychapterstyle}{%
    \renewcommand{\chapnamefont}{\LARGE\rmfamily\bfseries}%
    \renewcommand{\chapnumfont}{\LARGE\rmfamily\bfseries}%
    \renewcommand{\chaptitlefont}{\Huge\rmfamily\bfseries}%
    \renewcommand{\printchaptertitle}[1]{%
        \chaptitlefont\hrule height 0.5pt \vspace{1em}%
        {##1}\vspace{1em}\hrule height 0.5pt%
        }%
    \renewcommand{\printchapternum}{%
        \chapnumfont\thechapter%
        }%
}

\chapterstyle{mychapterstyle}

\setsecheadstyle{\Large\rmfamily\bfseries}
\setsubsecheadstyle{\large\rmfamily\bfseries}
\setsubsubsecheadstyle{\normalfont\rmfamily\bfseries}
\setparaheadstyle{\normalfont\rmfamily}

\makeevenhead{headings}{\thepage}{}{\small\slshape\leftmark}
\makeoddhead{headings}{\small\slshape\rightmark}{}{\thepage}

% ********* Table of contents style **********
\settocdepth{subsection}

\setsecnumdepth{subsection}
\maxsecnumdepth{subsection}
\settocdepth{subsection}
\maxtocdepth{subsection}

\renewcommand{\listfigurename}{List of Figures}
\renewcommand{\listtablename}{List of Tables}

% ********* General page styles **********

%Get the correct line spacing. Note that \onehalfspacing DOES NOT work because of the way which LaTeX measures linespacing (which is different to Word).
\linespread{1.3}
%Make sure footnotes don't split over a page.
\interfootnotelinepenalty=10000

%*************************************
% Fix white space to improve readability
%*************************************
%Redefine the sqrt command so that it puts a space after the surd.
%This makes AMSMATH much easier to read.
%COMMENT THIS OUT OR DELETE IF YOU DON'T WISH TO USE IT.
\let\SQRT\sqrt
\renewcommand{\sqrt}[1]{\ensuremath{\SQRT{#1} \;}}