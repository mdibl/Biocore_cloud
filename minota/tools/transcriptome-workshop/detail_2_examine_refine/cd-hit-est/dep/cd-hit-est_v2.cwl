class: CommandLineTool
cwlVersion: v1.0

baseCommand: [ cd-hit-est ]
inputs:
  - id: single_reads
    type: File
    inputBinding:
      position: 1
      prefix: '-i'
  - id: output_filename
    type: string
    inputBinding:
      position: 2
      prefix: '-o'
  - id: seq_id_threshold
    type: float
    default: 0.9
    inputBinding:
      position: 3
      prefix: '-c'
  - id: word_length
    type: int
    default: 10
    inputBinding:
      position: 4
      prefix: '-n'
  - id: cdhit_max_memory
    type: int
    default: 1600
    inputBinding:
      position: 5
      prefix: '-M'
  - id: cdhit_max_cpu
    type: int
    default: 8
    inputBinding:
      position: 6
      prefix: '-T'
outputs:
  - id: cluster_dir
    type: Directory
    outputBinding:
      glob: "$(inputs.output_filename).clstr"
  - id: rep_seq
    type: File
    outputBinding:
      glob: "$(inputs.output_filename)"
