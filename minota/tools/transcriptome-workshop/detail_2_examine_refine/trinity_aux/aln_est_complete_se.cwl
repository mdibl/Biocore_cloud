class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  edam: 'http://edamontology.org/'
  s: 'http://schema.org/'

requirements:
  SchemaDefRequirement:
    types:
      - $import: trinity-ss_lib_type.yaml
      - $import: trinity-seq_type.yaml
      - $import: trinity-est_method.yaml
      - $import: trinity-aln_method.yaml

baseCommand: [ /opt/software/external/trinity/trinity/util/align_and_estimate_abundance.pl ]
stdout: stdout.txt
stderr: stderr.txt
inputs:
  - id: transcripts
    type: File
    inputBinding:
      position: 1
      prefix: '--transcripts'
    label: 'transcript fasta file'
  - id: trinity_seq_type
    type: string
    default: fq
    inputBinding:
      position: 2
      prefix: '--seqType'
    label: 'fq|fa'
  - id: single_reads
    type: File
    inputBinding:
      position: 3
      prefix: '--single'
      itemSeparator: ","
    label: 'single read files (separated by commas, no spaces)'
  - id: trinity_est_method
    type: string
    inputBinding:
      position: 4
      prefix: '--est_method'
    label: 'abundance estimation method
            alignment based: RSEM|eXpress
            alignment free: kallisto|salmon'
  - id: trinity_aln_method
    type: string
    inputBinding:
      position: 5
      prefix: '--aln_method'
    label: 'alignment method'
  - id: trinity_mode
    type: boolean?
    inputBinding:
      position: 6
      prefix: '--trinity_mode'
    label: 'automatically generate gene_trans_map and utilize'
  - id: prep_reference
    type: boolean?
    inputBinding:
      position: 7
      prefix: '--prep_reference'
    label: 'prepare reference, constructs target index'
  - id: output_dir
    type: string
    inputBinding:
      position: 8
      prefix: '--output_dir'
    label: 'write all files to given output directory'
outputs:
  - id: aln_and_est_dir
    label: Alignment and estimation directory containing results
    type: Directory
    outputBinding:
      glob: "."
doc: >
  "Trinity, developed at the Broad Institute and the Hebrew University of
  Jerusalem,  represents a novel method for the efficient and robust de novo
  reconstruction  of transcriptomes from RNA-seq data.  Trinity combines three
  independent software modules: Inchworm, Chrysalis, and  Butterfly, applied
  sequentially to process large volumes of RNA-seq reads.

  Documentation at https://github.com/trinityrnaseq/trinityrnaseq/wiki"

label: 'A component of the Trinity toolkit, used to align reads
        and estimate gene abundance to generated transcript.'

hints:
  - class: SoftwareRequirement
    packages:
      Trinity:
        version:
          - 2.8.5
  - class: DockerRequirement
    dockerPull: 'trinityrnaseq/trinityrnaseq:2.8.5'

$schemas:
  - 'http://edamontology.org/EDAM_1.16.owl'
  - 'https://schema.org/docs/schema_org_rdfa.html'
s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:copyrightHolder: "MDI Biological Laboratory, 2019"
s:author: "Nathaniel Maki"
