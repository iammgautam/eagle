<template>
  <div class="bg-white font-epilogue">
    <form @submit.prevent="validateAndGenerate" class="px-4 sm:px-8 py-4">
      <div class="legalissue">
        <div class="flex flex-col items-center">
          <div class="w-full md:w-2/3 relative">
            <h2 class="text-zinc-500 text-sm mb-2 font-inter">LEGAL ISSUE</h2>
            <textarea name="legalIssue" ref="legalIssueRef"
              class="w-full h-24 sm:h-32 md:h-40 lg:h-48 p-4 text-l font-semibold placeholder-zinc-500 rounded-lg resize-none"
              placeholder="What is the legal issue?" style="font-size: 28px"></textarea>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mt-10">
        <div class="casefacts">
          <h1 class="text-lg sm:text-xl md:text-2xl font-regular text-black mb-4 relative">
            <span class="relative block">
              <h2 class="text-zinc-700 text-sm" style="font-family: Inter, sans-serif">FACTS</h2>
              <h2 class="text-zinc-500 text-sm bb-2" style="font-family: Inter, sans-serif">Please enter the brief facts
                of the case. You can type or paste relevant information, or upload documents such as First Information
                Reports, charge sheets, witness statements, and post-mortem reports.</h2>
            </span>
          </h1>
          <!-- <div class="mb-4">
            <label for="factsFiles" class="sr-only">Choose files</label>
            <input type="file" name="factsFiles" id="factsFiles" multiple
              class="block w-full border border-gray-200 shadow-sm rounded-lg text-sm focus:z-10 focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none file:bg-gray-50 file:border-0 file:me-4 file:py-3 file:px-4"
              accept=".pdf" />
          </div> -->
          <div class="flex flex-col relative">
            <div class="w-full">
              <textarea name="caseFacts" ref="caseFactsRef"
                class="w-full h-[280px] sm:h-[280px] lg:h-[300px] p-4 text-l placeholder-zinc-500 border border-black rounded-lg bg-[#fffbf7] bg-opacity-25 shadow-lg resize-none focus:outline-none focus:ring-2"
                :class="{ 'focus:ring-red-400': wordLimitExceeded }" placeholder="Type the facts of the case"
                style="font-size: 20px" @input="updateWordCount" v-model="caseFactsText"></textarea>
            </div>
            <div class="absolute bottom-2 right-4 text-gray-400">
              {{ wordCount }}/25000
            </div>
          </div>
        </div>

        <div class="legalresearch">
          <h1 class="text-lg sm:text-xl md:text-2xl font-regular text-black mb-4 relative">
            <span class="relative block">
              <h2 class="text-zinc-700 text-sm" style="font-family: Inter, sans-serif">LEGAL RESEARCH</h2>
              <h2 class="text-zinc-500 text-sm mb-2" style="font-family: Inter, sans-serif">Please provide relevant case
                law or legal judgments you wish to include in your legal memorandum. You can include specific case
                details, citations, or any pertinent legal decisions that support your legal memorandum.</h2>
            </span>
          </h1>
          <!-- <div class="mb-4">
            <label for="researchFiles" class="sr-only">Choose files</label>
            <input type="file" name="researchFiles" id="researchFiles" multiple
              class="block w-full border border-gray-200 shadow-sm rounded-lg text-sm focus:z-10 focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none file:bg-gray-50 file:border-0 file:me-4 file:py-3 file:px-4"
              accept=".pdf" />
          </div> -->
          <div class="flex flex-col relative">
            <div class="w-full">
              <textarea name="legalResearch" ref="legalResearchRef"
                class="w-full h-[280px] sm:h-[280px] lg:h-[300px] p-4 text-l placeholder-zinc-500 border border-black rounded-lg bg-[#fffbf7] bg-opacity-25 shadow-lg resize-none focus:outline-none focus:ring-2"
                :class="{ 'focus:ring-red-400': researchLimitExceeded }" placeholder="Add legal research"
                style="font-size: 20px" @input="updateResearchCount" v-model="legalResearchText"></textarea>
            </div>
            <div class="absolute bottom-2 right-4 text-gray-400">
              {{ researchCount }}/25000
            </div>
          </div>
        </div>
      </div>

      <div class="flex justify-center mt-6">
        <button class="bg-[#050142] text-[#C3E2EF] px-6 py-3 rounded-full text-l" @click="validateAndGenerate">
          Generate Memo
        </button>
      </div>
    </form>

    <!-- Data Validation Popup -->
    <div v-if="showDataValidationPopup"
      class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div class="bg-white rounded-lg shadow-lg p-6 flex flex-col items-center">
        <p class="text-lg text-center mb-4">Please enter data or upload files before generating the memo.</p>
        <button class="bg-[#050142] text-[#C3E2EF] px-4 py-2 rounded-md" @click="showDataValidationPopup = false">
          OK
        </button>
      </div>
    </div>

    <!-- Email Confirmation Popup -->
    <div v-if="showEmailPopup" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div class="bg-white rounded-lg shadow-lg p-6 flex flex-col items-center">
        <img src="../assets/email.png" alt="Logo" class="w-20 h-20 mb-4">
        <p class="text-lg text-center mb-4">You will receive an email at the address you used to sign up within 30 to 45
          minutes.</p>
        <button class="bg-[#050142] text-[#C3E2EF] px-4 py-2 rounded-md" @click="showEmailPopup = false">
          Okay, I will check my email in 30-45 minutes
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from "vue";

export default defineComponent({
  name: "CaseDetails",

  setup() {
    const legalIssueRef = ref<HTMLTextAreaElement | null>(null);
    const caseFactsRef = ref<HTMLTextAreaElement | null>(null);
    const legalResearchRef = ref<HTMLTextAreaElement | null>(null);
    const showDataValidationPopup = ref(false);
    const showEmailPopup = ref(false);

    const validateAndGenerate = () => {
      const legalIssue = legalIssueRef.value?.value.trim() || "";
      const caseFacts = caseFactsRef.value?.value.trim() || "";
      const legalResearch = legalResearchRef.value?.value.trim() || "";
      const factsFiles = document.getElementById("factsFiles") as HTMLInputElement;
      const researchFiles = document.getElementById("researchFiles") as HTMLInputElement;

      if (!legalIssue) {
        showDataValidationPopup.value = true;
        return; // Exit the function early if legal issue is not provided
      }

      if (!caseFacts && !legalResearch && factsFiles.files?.length === 0 && researchFiles.files?.length === 0) {
        showDataValidationPopup.value = true;
      } else {
        showEmailPopup.value = true;
      }
    };

    const caseFactsText = ref("");
    const legalResearchText = ref("");

    const wordCount = computed(() => {
      const words = caseFactsText.value.trim().split(/\s+/);
      return words.length;
    });

    const researchCount = computed(() => {
      const words = legalResearchText.value.trim().split(/\s+/);
      return words.length;
    });

    const wordLimitExceeded = computed(() => wordCount.value > 25000);
    const researchLimitExceeded = computed(() => researchCount.value > 25000);

    const updateWordCount = () => {
      if (wordCount.value > 25000) {
        caseFactsText.value = caseFactsText.value.slice(0, -1);
      }
    };

    const updateResearchCount = () => {
      if (researchCount.value > 25000) {
        legalResearchText.value = legalResearchText.value.slice(0, -1);
      }
    };

    return {
      legalIssueRef,
      caseFactsRef,
      legalResearchRef,
      validateAndGenerate,
      showDataValidationPopup,
      showEmailPopup,
      caseFactsText,
      legalResearchText,
      wordCount,
      researchCount,
      wordLimitExceeded,
      researchLimitExceeded,
      updateWordCount,
      updateResearchCount,
    };
  },
});
</script>

<style>
.legalissue textarea,
.casefacts textarea,
.legalresearch textarea {
  font-family: "Inter", sans-serif;
}

.cursor {
  position: absolute;
  top: 20px;
  left: 20px;
  width: 2px;
  height: 30px;
  background-color: #000;
  animation: blink 1s infinite;
}

@keyframes blink {

  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0;
  }
}
</style>