class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  edam: 'http://edamontology.org/'
  s: 'http://schema.org/'

baseCommand: [ hmmsearch ]
inputs:
  - id: tblout
    type: string
    default: hmmsearch.out
    inputBinding:
      position: 1
      prefix: '--tblout'
    label: 'save tabular file, summarzing per-target output'
  - id: noali
    type: boolean
    default: true
    inputBinding:
      position: 2
      prefix: '--noali'
    label: 'omit alignment section from main output, may greatly reduces output volume'
  - id: domtblout
    type: string
    default: domtbl.out
    inputBinding:
      position: 3
      prefix: '--domtblout'
    label: 'save tabular file, summarizing per-domain output'
  - id: cut_tc
    type: boolean
    default: true
    inputBinding:
      position: 4
      prefix: '--cut_tc'
    label: 'use TC (trusted cutoff) score threshold'
  - id: cpu
    type: int
    default: 8
    inputBinding:
      position: 5
      prefix: '--cpu'
    label: 'parallel threads utilized'
  - id: Z
    type: int
    default: 10000
    inputBinding:
      position: 6
      prefix: '-Z'
    label: 'assert total num of targets is (x), for per seq E-val calc'
  - id: db
    type: File
    inputBinding:
      position: 7
  - id: query
    type: File
    inputBinding:
      position: 8
  - id: fasta_flag
    type: File?
  - id: gff_flag
    type: File?

outputs:
  - id: hmmsearch_out
    type: File
    outputBinding:
      glob: "hmmsearch.out"
  - id: hmmdom_out
    type: File
    outputBinding:
      glob: "domtbl.out"


$schemas:
  - 'http://edamontology.org/EDAM_1.16.owl'
  - 'https://schema.org/docs/schema_org_rdfa.html'
s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:copyrightHolder: "MDI Biological Laboratory, 2019"
s:author: "Nathaniel Maki"