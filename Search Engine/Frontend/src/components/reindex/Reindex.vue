<template>
	<div>
	<standard-navbar/>
	<b-card header-tag="header" class="mt-5">
		<template #header>
			<h5>Reindex the entire database</h5>
		</template>
		<div class="overflow-auto justify-content-center">
			<b-button pill size="sm" variant="danger" class="mb-1" @click="regenerateIndexIssues()">
				Regenerate Issue List Database Index
			</b-button>
		</div>
	</b-card>
	<b-card header-tag="header" class="mt-5">
		<template #header>
			<h5>Reindex a set of issue IDs</h5>
		</template>
		<div class="overflow-auto justify-content-center">
			<p>
				Please enter the issues you wish to reindex, separated by a comma.
			</p>
			<b-row class="d-flex pb-4">
				<b-col align-self="center">
					<b-input-group class="ms-1 ">
						<b-form-input id="issues-csv" v-model="issueList" placeholder="TAG-1234,TAG-5678"></b-form-input>
					</b-input-group>
				</b-col>
				<b-col>
					<b-button pill size="sm" variant="danger" class="mb-1" @click="regenerateIndexIssuesCSV()">
						Reindex for these IDs
					</b-button>
				</b-col>
			</b-row>
		</div>
	</b-card>
	<b-card header-tag="header" class="mt-5">
		<template #header>
			<h5>Upload classification</h5>
		</template>
		<div class="overflow-auto justify-content-center">
			<p>
				Upload a .csv file, fill in the custom tag (leave blank for none) and press the button to mass-classify issues.
			</p>
			<b-row class="d-flex pb-4">
				<b-col>
					<input type="file" class="input-file" @change="previewFiles" accept="text/csv">
				</b-col>
				<b-col>
					<b-input-group class="ms-1 ">
						<b-form-input id="classific" v-model="classific_tag" placeholder="e.g. MAVEN"></b-form-input>
					</b-input-group>
				</b-col>
				<b-col>
					<b-button pill size="sm" variant="danger" class="mb-1" @click="uploadClassification()">
						Upload this classification
					</b-button>
				</b-col>
			</b-row>
		</div>
	</b-card>
	</div>
</template>

<script>
import StandardNavbar from "@/components/navbar/StandardNavbar";
import axios from "axios";

const url = process.env.VUE_APP_ARCHEDETECOR_API

export default {
	name: 'Reindex',
	components: {
		StandardNavbar
	},
	methods: {
		regenerateIndexIssues(){
			if (confirm("Are you sure you want to reindex the issue database? This might take a while.")) {
				axios.post(url + "issues/reindex").then(() => {
					this.$router.push({name: 'Home'})
				})
			}
		},
		regenerateIndexIssuesCSV(){
			let issues = []
			this.issueList.split(',').forEach(id => {
				issues.push(id.trim())
			})
			axios.post(url + "issue/reindex", issues).then(() => {
					this.$router.push({name: 'Home'})
			})
		},
		uploadClassification(){
			console.log(this.classific_tag)
			console.log(this.file)
			const formData = new FormData();
			formData.append("file", this.file)
			formData.append("newTag", this.classific_tag)
			axios.post(url + "tag/upload", formData, {
				headers: {
					'Content-Type': 'multipart/form-data'
				}
			}).then(() => {
				this.$router.push({name: 'Home'})
			}).catch((err) => {
				console.log(err)
			})
		},
		previewFiles(event){
			console.log(event.target.files);
			this.file = event.target.files[0]
		}
	}
}
</script>

<style scoped>
</style>