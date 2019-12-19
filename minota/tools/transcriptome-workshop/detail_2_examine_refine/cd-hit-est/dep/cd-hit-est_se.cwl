class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  edam: 'http://edamontology.org/'
  s: 'http://schema.org/'

baseCommand: [ cd-hit-est ]
inputs: 
  - id: single_reads
    type: File
    inputBinding:
      position: 1
      prefix: '-i'
      label: 'Single read(s)'
      doc: > "input filename(s) in fasta format, single read(s)"
	- id: output_filename
		type: string
		inputBinding:
			position: 2
			prefix: '-o'
		label: 'Output filename'
		doc: > "Name of output file, required"
	- id: seq_id_threshold
		type: float
		default: 0.9
		inputBinding:
			position: 3
			prefix: '-c'
		label: 'Sequence identity threshold'
		doc: > "default cd-hits global seq identity, calculated as
						number of identical bases in alignment / by full length
						of shorter sequence"
	- id: word_length
		type: int?
		default: 10
		inputBinding:
			position: 4
			prefix: '-n'
		label: 'Word length'
		doc: > "TODO: read Users guide for word_length"
	- id: clstr_desc_len
		type: string
		default: 20
		inputBinding:
			position: 5
			prefix: '-d'
		label: 'Cluster file description length'
		doc: > "If set to 0, will take fasta defline, stop at 1st space"
	- id: cdhit_max_memory
		type: int?
		default: 4096
		inputBinding:
			position: 6
			prefix: '-M'
		label: 'Memory limit (in MB)'
		doc: > "If set to 0, memory will be unlimited"
	- id: cdhit_max_cpu
		type: int?
		default: 8
		inputBinding:
			position: 7
			prefix: '-T'
		label: 'Thread limit'
		doc: > "Number of threads, with 0 all CPUs will be used"
outputs:
	-	id: cluster_dir
		label: 'Contains representative seq(s), text file of list of clusters'
		type: Directory
		outputBinding:
			glob: "."
	- id: rep_seq
		label: 'Representative sequences'
		type: File
		outputBinding:
			glob: "*fasta"
			
label:  Clusters nucleotide dataset into bundles that fit a custom similarity threshold

doc: > 
	"CD-HIT-EST clusters a nucleotide dataset into clusters that meet a user-defined similarity threshold, 
	usually a sequence identity. The input is a DNA/RNA dataset in fasta format and the output are two files: 
	a fasta file of representative sequences and a text file of list of clusters. Since eukaryotic genes usually 
	have long introns, which cause long gaps, it is difficult to make full-length alignments for these genes. So, 
	CD-HIT-EST is good for non-intron containing sequences like EST.

	Documentation can be found at: https://github.com/weizhongli/cdhit/wiki/3.-User's-Guide#CDHITEST"

hints:
	-	class: DockerRequirement
		dockerPull: 'biocontainers/cd-hit'

$schemas:
  - 'http://edamontology.org/EDAM_1.16.owl'
  - 'https://schema.org/docs/schema_org_rdfa.html'
s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:copyrightHolder: "MDIBL - MDI Biological Laboratory, 2019"
s:author: "Nathaniel Maki"
