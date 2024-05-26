<template>
  <div class="bg-white font-epilogue">
    <h1 class="text-xl sm:text-2xl md:text-3xl font-regular text-black px-4 sm:px-8 py-4 relative">
      <span class="relative block">
        <span class="relative z-10">Enter the case Details</span>
        <span
          class="absolute left-3 sm:left-4 -top-1 sm:-top-3 w-8 h-8 sm:w-10 sm:h-10 md:w-12 md:h-12 bg-[#70D5FF] rounded-full opacity-80 z-0"></span>
      </span>
    </h1>




    <form @submit.prevent="handleSubmit" class="px-4 sm:px-8 py-4">
      <div class="casetitle">
        <h1 class="text-lg sm:text-xl md:text-2xl font-regular text-black mt-4 mb-4 relative">
          <span class="relative block">
            <h2 class="text-zinc-500 text-sm" style="font-family: Inter, sans-serif">CASE TITLE</h2>
          </span>
        </h1>
        <div class="flex flex-col md:flex-row items-center justify-between">
          <div class="w-full md:w-auto">
            <textarea name="petitionerName" ref="petitionerRef"
              class="w-full md:w-[200px] lg:w-[420px] h-14 p-4 text-l placeholder-zinc-500 border border-black rounded-lg bg-[#fffbf7] bg-opacity-25 shadow-lg resize-none overflow-hidden"
              placeholder="Petitioner's Name" style="font-size: 20px"></textarea>
          </div>
          <div class="mx-2 text-xl sm:text-2xl font-semibold">v.</div>
          <div class="w-full md:w-auto">
            <textarea name="respondentName" ref="respondentRef"
              class="w-full md:w-[200px] lg:w-[420px] h-14 p-4 text-l placeholder-zinc-500 border border-black rounded-lg bg-[#fffbf7] bg-opacity-25 shadow-lg resize-none overflow-hidden"
              placeholder="Respondent's Name" style="font-size: 20px"></textarea>
          </div>
          <div class="mx-2 text-xl sm:text-2xl font-semibold">in</div>
          <div class="w-full md:w-auto">
            <button
              class="w-full md:w-[200px] lg:w-[420px] h-14 p-4 mb-2 text-l placeholder-zinc-500 border border-black rounded-lg bg-[#fffbf7] bg-opacity-25 shadow-lg resize-none"
              style="font-size: 20px" @click.stop="showCourtDropdown = !showCourtDropdown">
              {{ selectedCourt || "Select Court" }}
            </button>
            <div v-if="showCourtDropdown" class="fixed top-0 right-0 w-full h-full z-50 flex justify-end pt-20"
              @click.self="showCourtDropdown = false">
              <div
                class="bg-white rounded-lg shadow-lg p-6 w-full sm:w-[460px] max-h-190 overflow-y-auto custom-scrollbar">
                <input type="text" v-model="courtSearchQuery" placeholder="Search for courts" @input="filterCourts"
                  class="w-full mb-4 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
                <ul class="court-list">
                  <li v-for="(court, index) in visibleCourts" :key="court" @click="
                    selectCourt(court);
                  showCourtDropdown = false;
                  " :class="{ 'selected-court': selectedCourt === court }"
                    class="cursor-pointer py-2 px-4 rounded-lg hover:text-[#050142] hover:font-medium transition-colors text-[#686868]"
                    :style="{ animationDelay: `${index * 0.1}s` }">
                    {{ court }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="casefacts">
          <h1 class="text-lg sm:text-xl md:text-2xl font-regular text-black mt-10 mb-4 relative">
            <span class="relative block">
              <h2 class="text-zinc-500 text-sm" style="font-family: Inter, sans-serif">BRIEF FACT</h2>
            </span>
          </h1>
          <div class="flex flex-col relative">
            <div class="w-full">
              <textarea name="caseFacts" ref="caseFactsRef"
                class="w-full h-[300px] sm:h-[400px] lg:h-[500px] p-4 text-l placeholder-zinc-500 border border-black rounded-lg bg-[#fffbf7] bg-opacity-25 shadow-lg resize-none focus:outline-none focus:ring-2"
                :class="{ 'focus:ring-red-400': wordLimitExceeded }" placeholder="Type the facts of the case"
                style="font-size: 20px" @input="updateWordCount" v-model="caseFactsText"></textarea>
            </div>
            <div class="absolute bottom-2 right-4 text-gray-400">
              {{ wordCount }}/25000
            </div>
          </div>
        </div>

        <div class="flex flex-col gap-8">
          <div class="legalissue">
            <h1 class="text-lg sm:text-xl md:text-2xl font-regular text-black mt-10 mb-4 relative">
              <span class="relative block">
                <h2 class="text-zinc-500 text-sm" style="font-family: Inter, sans-serif">LEGAL ISSUE</h2>
              </span>
            </h1>
            <div class="flex flex-col">
              <div class="w-full">
                <textarea name="legalIssue" ref="legalIssueRef"
                  class="w-full h-24 sm:h-32 md:h-40 lg:h-[90px] p-4 text-l placeholder-zinc-500 border border-black rounded-lg bg-[#fffbf7] bg-opacity-25 shadow-lg resize-none"
                  placeholder="What is the legal issue?" style="font-size: 20px"></textarea>
              </div>
            </div>
          </div>

          <div>
            <div class="max-w-full">
              <div class="mb-2">
                <h2 class="text-zinc-500 text-sm" style="font-family: Inter, sans-serif">ATTACHMENT</h2>
                <p class="text-zinc-500 text-xs">Upload any relevant files of the case</p>
              </div>
              <label for="file-input-1" class="sr-only">Choose file 1</label>
              <input type="file" name="file-input-1" id="file-input-1"
                class="block w-full border border-gray-200 shadow-sm rounded-lg text-sm focus:z-10 focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none file:bg-gray-50 file:border-0 file:me-4 file:py-3 file:px-4"
                accept=".pdf" @change="validateFile('fileError1', $event)" />
              <div v-if="fileError1" class="text-red-500 mt-2">{{ fileError1 }}</div>
              <div class="mt-4 mb-2">
                <h2 class="text-zinc-500 text-sm" style="font-family: Inter, sans-serif">RESEARCH</h2>
                <p class="text-zinc-500 text-xs">Upload any relevant files of the case</p>
              </div>
              <label for="file-input-2" class="sr-only mt-4">Choose file 2</label>
              <input type="file" name="file-input-2" id="file-input-2"
                class="block w-full border border-gray-200 shadow-sm rounded-lg text-sm focus:z-10 focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none file:bg-gray-50 file:border-0 file:me-4 file:py-3 file:px-4"
                accept=".pdf" @change="validateFile('fileError2', $event)" />
              <div v-if="fileError2" class="text-red-500 mt-2">{{ fileError2 }}</div>
              <p class="text-zinc-500 text-xs mt-3">**please do not upload any files as they are not processed</p>
            </div>
            <div class="flex flex-col items-start mt-10">
              <h2 class="text-zinc-500 text-sm mb-4" style="font-family: Inter, sans-serif">GENERATE</h2>
              <div class="flex flex-col sm:flex-row justify-start">
                <button
                  class="flex items-center justify-center text-l border border-black rounded-full px-6 py-3 mr-4 mb-4 sm:mb-0 hover:text-[#C3E2EF] hover:bg-[#050142] hover:border-transparent"
                  @click="validateAndProceed('petitioner')">
                  Petitioner
                </button>

                <button
                  class="flex items-center justify-center text-l border border-black rounded-full px-6 py-3 hover:text-[#ffffff] hover:bg-[#E72929] hover:border-transparent"
                  @click="validateAndProceed('respondent')">
                  Respondent
                </button>
              </div>
            </div>
          </div>

        </div>
      </div>
    </form>
    <!-- Contact and Feedback buttons -->
    <div class="fixed bottom-4 right-4 flex">
      <div class="relative">
        <button class="text-sm text-gray-500 hover:text-black hover:underline" @click="showContactPopup = true">
          Contact
        </button>
        <div v-if="showContactPopup"
          class="absolute bottom-full left-1/2 transform -translate-x-1/2 bg-white p-4 rounded-md shadow-md">
          <p>Contact Information:</p>
          <p>Email: contact@example.com</p>
          <p>Phone: 123-456-7890</p>
          <button class="mt-2 text-sm text-gray-500 hover:text-black hover:underline" @click="showContactPopup = false">
            Close
          </button>
        </div>
      </div>
      <a href="https://example.com/feedback" target="_blank"
        class="ml-4 text-sm text-gray-500 hover:text-black hover:underline">
        Feedback
      </a>
    </div>

    <!-- Email Confirmation Popup -->
    <div v-if="showEmailPopup" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div class="bg-white rounded-lg shadow-lg p-6 flex flex-col items-center">
        <img src="../assets/email.png" alt="Logo" class="w-20 h-20 mb-4">
        <p class="text-lg text-center mb-4">You will receive an email at the address you used to sign up within 10 to 15
          minutes. Please check your email and follow the instructions.</p>
        <button class="bg-[#050142] text-[#C3E2EF] px-4 py-2 rounded-md" @click="showEmailPopup = false">
          Okay, I will check my email in 10-15 minutes
        </button>
      </div>
    </div>

  </div>
</template>



<script lang="ts">
import router from "@/router";
import { computed, defineComponent, onMounted, Ref, ref } from "vue";

const highCourts = [
  "Supreme Court of India",
  "Allahabad High Court",
  "Andhra Pradesh High Court",
  "Bombay High Court",
  "Calcutta High Court",
  "Chhattisgarh High Court",
  "Delhi High Court",
  "Gauhati High Court",
  "Gujarat High Court",
  "Himachal Pradesh High Court",
  "Jammu and Kashmir High Court",
  "Jharkhand High Court",
  "Karnataka High Court",
  "Kerala High Court",
  "Madhya Pradesh High Court",
  "Madras High Court",
  "Manipur High Court",
  "Meghalaya High Court",
  "Orissa High Court",
  "Patna High Court",
  "Punjab and Haryana High Court",
  "Rajasthan High Court",
  "Sikkim High Court",
  "Telangana High Court",
  "Tripura High Court",
  "Uttarakhand High Court",
];


export default defineComponent({
  name: "CaseDetails",

  setup() {
    const petitionerRef: Ref<HTMLTextAreaElement | null> = ref(null);
    const respondentRef: Ref<HTMLTextAreaElement | null> = ref(null);
    const caseFactsRef: Ref<HTMLTextAreaElement | null> = ref(null);
    const legalIssueRef: Ref<HTMLTextAreaElement | null> = ref(null);
    const showCourtDropdown = ref(false);
    const selectedCourt = ref(null);
    const courtSearchQuery = ref("");
    const visibleCourts = ref(highCourts);
    const showContactPopup = ref(false);
    const showEmailPopup = ref(false);


    const filterCourts = () => {
      const query = courtSearchQuery.value.toLowerCase();
      visibleCourts.value = highCourts.filter((court) =>
        court.toLowerCase().includes(query)
      );
    };

    const selectCourt = (court: any) => {
      selectedCourt.value = court;
    };

    onMounted(() => {
      // Scroll to the top of the page
      window.scrollTo(0, 0);
    });
    const validateAndProceed = (role: "petitioner" | "respondent") => {
      // Safely accessing the value properties of the textarea elements
      const petitionerName = petitionerRef.value?.value.trim() || "";
      const respondentName = respondentRef.value?.value.trim() || "";
      const caseFacts = caseFactsRef.value?.value.trim() || "";
      const legalIssue = legalIssueRef.value?.value.trim() || "";

      // Check if the word limit is exceeded
      const wordCount = caseFacts.split(/\s+/).length;
      const wordLimitExceeded = wordCount > 25000;

      // Update the focus ring color if the word limit is exceeded
      if (wordLimitExceeded) {
        caseFactsRef.value?.classList.add("focus-ring-red");
      } else {
        caseFactsRef.value?.classList.remove("focus-ring-red");
      }

      const isAnyFieldEmpty = !petitionerName || !respondentName || !caseFacts || !legalIssue;

      if (isAnyFieldEmpty) {
        const missingFields = [];
        if (!petitionerName) missingFields.push("Petitioner Name");
        if (!respondentName) missingFields.push("Respondent Name");
        if (!caseFacts) missingFields.push("Case Facts");
        if (!legalIssue) missingFields.push("Legal Issue");
        alert(`Please enter the following fields: ${missingFields.join(", ")}`);
        return;
      }

      // Show the exceeded word limit popup if applicable
      if (wordLimitExceeded && (role === "petitioner" || role === "respondent")) {
        alert("Exceeded word limit in Brief Facts. Please reduce the word count.");
        return;
      }

      // Show the email confirmation popup
      showEmailPopup.value = true;
    };

    const handleSubmit = (event: Event, role?: "petitioner" | "respondent") => { event.preventDefault(); };



    const fileError1 = ref('');
    const fileError2 = ref('');

    const validateFile = (errorRef: 'fileError1' | 'fileError2', event: Event) => {
      const file = (event.target as HTMLInputElement).files?.[0];
      const maxSize = 100 * 1024 * 1024; // 100MB in bytes

      // Reset the file error
      if (errorRef === 'fileError1') {
        fileError1.value = '';
      } else {
        fileError2.value = '';
      }

      if (!file) {
        return;
      }

      // Check if the file type is PDF
      if (!file.type.includes('pdf')) {
        if (errorRef === 'fileError1') {
          fileError1.value = 'Only PDF files are allowed.';
        } else {
          fileError2.value = 'Only PDF files are allowed.';
        }
        (event.target as HTMLInputElement).value = ''; // Clear the file input
        return;
      }

      // Check if the file size is within the limit
      if (file.size > maxSize) {
        if (errorRef === 'fileError1') {
          fileError1.value = 'The file size exceeds the limit of 100MB.';
        } else {
          fileError2.value = 'The file size exceeds the limit of 100MB.';
        }
        (event.target as HTMLInputElement).value = ''; // Clear the file input
        return;
      }

      // File is valid, you can proceed with further processing
      console.log('File is valid:', file);
    };

    const caseFactsText = ref('');
    const wordCount = computed(() => {
      const words = caseFactsText.value.trim().split(/\s+/);
      return words.length;
    });
    const wordLimitExceeded = computed(() => wordCount.value > 25000);

    const updateWordCount = () => {
      if (wordCount.value > 25000) {
        caseFactsText.value = caseFactsText.value.slice(0, -1);
      }
    };


    return {
      petitionerRef,
      respondentRef,
      caseFactsRef,
      legalIssueRef,
      validateAndProceed,
      showCourtDropdown,
      selectedCourt,
      courtSearchQuery,
      visibleCourts,
      filterCourts,
      selectCourt,
      handleSubmit,
      fileError1,
      fileError2,
      validateFile,
      showContactPopup,
      showEmailPopup,
      caseFactsText,
      wordCount,
      updateWordCount,
      wordLimitExceeded,
    };
  },
});
</script>

<style>
.respondentRef .petitionerRef textarea {
  font-family: "Inter", sans-serif;
}

.casefacts textarea {
  font-family: "Inter", sans-serif;
}

.legalissue textarea {
  font-family: "Inter", sans-serif;
}
</style>