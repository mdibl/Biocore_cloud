class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  edam: 'http://edamontology.org/'
  s: 'http://schema.org/'

baseCommand: [ blastp ]
hints:
  DockerRequirement:
    dockerPull: ncbi/blast
requirements:
- class: EnvVarRequirement
  envDef:
  - envName: BLASTDB
    envValue: $(inputs.blastdb_dir.path)
inputs:
  - id: blastdb_dir
    type: Directory?
  - id: transdecoder_pep
    type: File
    inputBinding:
      position: 1
      prefix: '-query'
    label: 'query file name'
  - id: database
    type: File
    inputBinding:
      position: 2
      prefix: '-db'
    label: 'BLAST database name'
  - id: num_threads
    type: int
    inputBinding:
      position: 3
      prefix: '-num_threads'
    label: 'number of threads for blastp'
  - id: max_target_seqs
    type: int
    inputBinding:
      position: 3
      prefix: '-max_target_seqs'
    label: 'number of aligned seq to keep, 
            norm default is 1, but Shad 2018 recommends 5'
  - id: outfmt
    type: int
    inputBinding:
      position: 4
      prefix: '-outfmt'
    label: 'alignment view options (6 denotes tabuler alignment view)'
  - id: e_value
    type: float
    inputBinding:
      position: 5
      prefix: '-evalue'
    label: 'expected value for saving hits'
  - id: out_flag
    type: string
    default: "blastp.outfmt6"
    inputBinding:
      position: 6
      prefix: '-out'
outputs:
  - id: blastp_output
    type: File
    outputBinding:
      glob: $(inputs.out_flag)
doc: >
  "Referenced paper: https://academic.oup.com/bioinformatics/article-abstract/35/9/1613/5106166"
  "Blast+ CLO: https://www.ncbi.nlm.nih.gov/books/NBK279684/"
  $schemas:
  - 'http://edamontology.org/EDAM_1.16.owl'
  - 'https://schema.org/docs/schema_org_rdfa.html'
s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:copyrightHolder: "MDI Biological Laboratory, 2019"
s:author: "Nathaniel Maki"