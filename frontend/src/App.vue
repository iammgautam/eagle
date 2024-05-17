<template>
    <div class="bg-white font-epilogue">
        <h1 class="text-3xl font-regular text-black px-8 py-4 relative">
            <span class="relative block">
                <span class="relative z-10">Enter the case title, facts and the legal issue</span>
                <span class="absolute left-3 -top-2 w-12 h-12 bg-[#70D5FF] rounded-full opacity-80 z-0"></span>
            </span>
        </h1>
        <div class="px-8 py-2 text-zinc-700 text-xl">
            <span>Kindly provide the title of the case, list the facts of the case in a point-wise format. Note that
                your case
                may involve multiple legal issues. Initially, enter only one legal issue; do not include more than one
                at this
                stage.</span>
        </div>

        <form class="px-8 py-4">
            <div class="casetitle">
                <h1 class="text-2xl font-regular text-black mt-10 mb-4 relative">
                    <span class="relative block">
                        <span class="relative z-10">Case title</span>
                    </span>
                </h1>
                <div class="flex items-center justify-between">
                    <div class="flex-1">
                        <textarea name="petitionerName" ref="petitionerRef" v-model="caseDetail.petitioner_name"
                            class="w-full h-14 p-4 text-l placeholder-zinc-500 border border-black rounded-lg bg-[#fffbf7] bg-opacity-25 shadow-lg resize-none overflow-hidden"
                            placeholder="Petitioner's Name" style="font-size: 20px;"></textarea>
                    </div>
                    <div class="mx-4 text-2xl font-bold">
                        vs
                    </div>
                    <div class="flex-1">
                        <textarea name="respondentName" ref="respondentRef" v-model="caseDetail.respondent_name"
                            class="w-full h-14 p-4 text-l placeholder-zinc-500 border border-black rounded-lg bg-[#fffbf7] bg-opacity-25 shadow-lg resize-none overflow-hidden"
                            placeholder="Respondent's Name" style="font-size: 20px;"></textarea>
                    </div>
                </div>
            </div>

            <div class="casefacts">
                <h1 class="text-2xl font-regular text-black mt-10 mb-4 relative">
                    <span class="relative block">
                        <span class="relative z-10">Facts of the case</span>
                    </span>
                </h1>
                <div class="flex flex-col">
                    <div class="w-full">
                        <textarea name="caseFacts" ref="caseFactsRef" v-model="caseDetail.fact_case"
                            class="w-full h-[750px] p-4 text-l placeholder-zinc-500 border border-black rounded-lg bg-[#fffbf7] bg-opacity-25 shadow-lg resize-none"
                            placeholder="Type the facts of the case" style="font-size: 20px;"></textarea>
                    </div>
                </div>
            </div>

            <div class="legalissue">
                <h1 class="text-2xl font-regular text-black mt-10 mb-4 relative">
                    <span class="relative block">
                        <span class="relative z-10">Legal Issue</span>
                    </span>
                </h1>
                <div class="flex flex-col">
                    <div class="w-full">
                        <textarea name="legalIssue" ref="legalIssueRef" v-model="caseDetail.legal_issue"
                            class="w-full h-[90px] p-4 text-l placeholder-zinc-500 border border-black rounded-lg bg-[#fffbf7] bg-opacity-25 shadow-lg resize-none"
                            placeholder="What is the legal issue?" style="font-size: 20px;"></textarea>
                    </div>
                </div>
            </div>

            <div class="flex justify-end mt-8 mb-8 mx-8">
                <button
                    class="flex items-center justify-center text-l text-[#C3E2EF] bg-[#050142] rounded-full px-6 py-3"
                    @click.prevent="submitForm">
                    Save and proceed
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-2" fill="none" viewBox="0 0 24 24"
                        stroke="#C3E2EF">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                </button>
            </div>
        </form>
    </div>

</template>

<!-- <script lang="ts">
// import router from '@/router';
import { defineComponent, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useCaseDetailsStore } from '@/stores/CaseDetailsStore';


export default defineComponent({
    name: 'CaseDetails',

    setup() {
        const petitionerRef = ref('');
        const respondentRef = ref('');
        const caseFactsRef = ref('');
        const legalIssueRef = ref('');
        const caseDetailsStore = useCaseDetailsStore();



        onMounted(() => {
            // Scroll to the top of the page
            window.scrollTo(0, 0);
        });

        const validateAndProceed = (event: Event) => {
            const form = event.target as HTMLFormElement;

            if (form instanceof HTMLFormElement) {
                const formData = new FormData(form);

                const petitionerName = formData.get('petitionerName')?.toString().trim() || '';
                const respondentName = formData.get('respondentName')?.toString().trim() || '';
                const caseFacts = formData.get('caseFacts')?.toString().trim() || '';
                const legalIssue = formData.get('legalIssue')?.toString().trim() || '';

                const isAnyFieldEmpty = !petitionerName || !respondentName || !caseFacts || !legalIssue;

                if (isAnyFieldEmpty) {
                    console.error('Invalid form element');
                } else {
                    caseDetailsStore.setPetitionerName(petitionerName);
                    caseDetailsStore.setRespondentName(respondentName);
                    caseDetailsStore.setCaseFacts(caseFacts);
                    caseDetailsStore.setLegalIssue(legalIssue);


                    // Navigate to SelectCategory
                    // router.push('/select-category');
                }
            }
        };


        return {
            petitionerRef,
            respondentRef,
            caseFactsRef,
            legalIssueRef,
            validateAndProceed,
        };
    }
});
</script> -->


<script>
import axios from 'axios'

export default {
    data() {
        return {
            caseDetail: {
                petitioner_name: '',
                respondent_name: '',
                legal_issue: '',
                fact_case: '',
            }
        }
    },
    methods: {
        submitForm() {
            console.log("What is the values,", this.caseDetail);
            axios.post('http://localhost:8000/api/case_history/casehistories/create_or_update/', this.caseDetail)
                .then(response => {
                    console.log(response.data.id)
                    // data = {
                    //     case_history: response.data.id
                    // };
                    axios.post('http://localhost:8000/api/brief_arguments/brief_arguments/create_or_update_brief_argument/', {case_history: response.data.id})
                    // handle successful response
                })
                .catch(error => {
                    console.error(error)
                    // handle error response
                })
        }
    }
}
</script>
<style scoped>
.logo {
    height: 6em;
    padding: 1.5em;
    will-change: filter;
    transition: filter 300ms;
}

.logo:hover {
    filter: drop-shadow(0 0 2em #646cffaa);
}

.logo.vue:hover {
    filter: drop-shadow(0 0 2em #42b883aa);
}
</style>