<template>
  <div class="gradient-box from-[#F1F0E8] to-[#ffffff] p-4">
    <div v-if="currentScreen === 1">
      <!-- Screen 1 -->
      <div class="relative flex flex-col items-center text-center mt-10 font-epilogue">
        <p class="text-[#28261B] mb-4 text-4xl lg:text-4xl">LexPlore</p>
        <p class="text-[#28261B] w-full text-base lg:text-xl -mt-3">
          India's most advanced legal research search box
        </p>
      </div>

      <div class="flex mt-60 items-center justify-center">
        <div class="relative w-full max-w-[900px]">
          <div class="flex items-center">
            <textarea ref="searchInput1" v-model="searchQuery" placeholder="Search..."
              class="search-input font-inter shadow-lg w-[850px] text-lg rounded-2xl pl-4 pr-20 py-2 border border-gray-400"
              @input="adjustHeight1" rows="1" style="
                height: auto;
                min-height: 60px;
                max-height: 15vh;
                overflow-y: auto;
              "></textarea>
            <button
              class="absolute font-inter left-[870px] shadow-lg top-[50px] h-[58px] w-[100px] transform -translate-y-1/2 px-4 py-2 rounded-2xl cursor-pointer"
              :class="{
                'bg-[#BA5B37] bg-opacity-85 text-[#FFFFFF]':
                  !searchQuery && !buttonHover,
                'bg-[#BA5B37] text-[#FFFFFF]': searchQuery || buttonHover,
              }" @mouseover="buttonHover = true" @mouseleave="buttonHover = false" @click="switchToScreen2">
              Search
            </button>
          </div>
          <div class="mt-4 text-center text-[#1F2837] font-epilogue">
            <div class="text-sm">
              <span class="sentence">{{ typedSentence }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else>
      <!-- Screen 2 -->
      <div class="relative flex flex-col items-center text-center font-epilogue">
        <p class="text-[#28261B] mb-4 text-3xl lg:text-4xl">LexPlore</p>
        <p class="text-[#28261B] w-full text-base lg:text-lg -mt-4">
          India's most advanced legal research search box
        </p>
      </div>
      <div class="flex flex-col items-center mt-2">
        <div class="relative w-full max-w-[750px]">
          <div class="flex items-center">
            <textarea ref="searchInput2" v-model="searchQuery" placeholder="Search..."
              class="search-input font-inter w-[700px] text-lg rounded-2xl pl-4 pr-12 py-2 border border-gray-400"
              @input="adjustHeight2" rows="1" style="
                height: auto;
                min-height: 42px;
                max-height: 9vh;
                overflow-y: auto;
              "></textarea>
            <button
              class="absolute font-inter left-[710px] top-[42px] transform -translate-y-1/2 w-10 h-10 rounded-xl flex items-center justify-center"
              :class="{
                'bg-[#BA5B37] bg-opacity-85 text-[#FFFFFF]':
                  !searchQuery && !buttonHover,
                'bg-[#BA5B37] text-[#FFFFFF]': searchQuery || buttonHover,
              }" @mouseover="buttonHover = true" @mouseleave="buttonHover = false">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 10l7-7m0 0l7 7m-7-7v18" />
              </svg>
            </button>
          </div>
        </div>
      </div>


      <div class="results flex border rounded-lg shadow-lg bg-[#F8F8F8] border-[#a8a8a8] mt-12 p-4 h-[540px] flex-col">
        <div class="flex flex-1">
          <div class="w-1/5 p-4 flex flex-col border-r border-gray-300">
            <h2 class="text-lg font-medium mb-3 -mt-4 text-left font-epilogue">Authority</h2>
            <div class="overflow-y-auto leading-relaxed text-[#050142] font-inter" style="max-height: 440px; font-size: 14px;">
              <ul>
                <li
                  v-for="(citation, index) in citations"
                  :key="index"
                  :class="[
                    'my-3 cursor-pointer',
                    {
                      'font-semibold text-[#050142] underline': index === selectedCitation,
                    },
                  ]"
                  @click="selectCitation(index)"
                >
                  {{ citation.title }}
                </li>
              </ul>
            </div>
          </div>
          <div class="w-2/6 p-4 flex flex-col border-r border-gray-300">
            <h2 class="text-lg font-medium mb-4 -mt-4 text-left font-epilogue">Case Note</h2>
            <div class="overflow-y-auto leading-relaxed text-[#050142] font-inter" style="max-height: 440px; font-size: 14px;">
              <div v-if="selectedCitation !== null">
                <p><strong>Case ID:</strong> {{ citations[selectedCitation].case_id }}</p>
                <p><strong>Judge Names:</strong> {{ citations[selectedCitation].judge_names }}</p>
                <p><strong>Cases Referred:</strong></p>
                <ul>
                  <li v-for="(case_referred, index) in citations[selectedCitation].cases_referred" :key="index">
                    {{ case_referred }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
          <div class="w-1/2 p-4 flex flex-col">
            <h2 class="text-lg font-medium mb-4 -mt-4 text-left font-epilogue font-inter">Content</h2>
            <div class="overflow-y-auto" style="max-height: 440px">
              <div v-if="selectedCitation !== null">
                <div
                  v-for="(content, index) in citations[selectedCitation].contents"
                  :key="index"
                  class="bg-[#F3F4ED] text-[#28261B] shadow-sm rounded-lg p-4 overflow-y-auto h-[180px] mb-4 leading-relaxed" style="font-size: 14px;"
                  @click="openReaderView(content)"
                >
                  {{ content }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <h2 class="text-[#28261B] text-center font-semibold font-inter mb-1 absolute bottom-0 left-1/2 transform -translate-x-1/2">SYNDICUS</h2>
  </div>

  <div v-if="showReaderView" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50" @click.self="closeReaderView">
    <div class="bg-white w-[180mm] h-[200mm] p-8 overflow-y-auto">
      <p class="text-gray-700 text-lg text-justify font-inter leading-relaxed">
        {{ selectedContent }}
      </p>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, nextTick } from "vue";

export default defineComponent({
  name: "UserMembership",
  setup() {
    const citations = ref([
      {
        title: "Wild Life (Protection) Act 1972 s 2",
        case_id: "Rithk Chowdary v. State of Andhra Pradesh Andhra Pradesh",
        judge_names: "Jishnu Sai M, Kailash Chad Rithik Chowdary, Mithelish Gautham",
        cases_referred: [
          "Case 1",
          "Case 2",
          "Case 3"
        ],
        contents: [
          "Content 1 of Wild Life (Protection) Act 1972 s 2Just enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issue",
          "Content 2 of Wild Life (Protection) Act 1972 s 2",
          "Content 3 of Wild Life (Protection) Act 1972 s 2"
        ]
      },
      {
        title: "Wild Life (Protection) Act 1972 s 2",
        case_id: "123",
        judge_names: "Judge 1, Judge 2",
        cases_referred: [
          "Case 1",
          "Case 2",
          "Case 3"
        ],
        contents: [
          "Content 1 of Wild Life (Protection) Act 1972 s 2Just enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issue",
          "Content 2 of Wild Life (Protection) Act 1972 s 2",
          "Content 3 of Wild Life (Protection) Act 1972 s 2"
        ]
      },
      {
        title: "Wild Life (Protection) Act 1972 s 2",
        case_id: "123",
        judge_names: "Judge 1, Judge 2",
        cases_referred: [
          "Case 1",
          "Case 2",
          "Case 3"
        ],
        contents: [
          "Content 1 of Wild Life (Protection) Act 1972 s 2Just enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issueJust enter the legal issue or a brief answer to any legal issue",
          "Content 2 of Wild Life (Protection) Act 1972 s 2",
          "Content 3 of Wild Life (Protection) Act 1972 s 2"
        ]
      },
      
      // ... (Other citations remain the same) ...
    ]);
    const selectedCitation = ref<number | null>(0);
    const searchQuery = ref("");
    const buttonHover = ref(false);
    const searchInput1 = ref<HTMLTextAreaElement | null>(null);
    const searchInput2 = ref<HTMLTextAreaElement | null>(null);

    const selectCitation = (index: number) => {
      selectedCitation.value = index;
    };

    const adjustHeight = (textarea: HTMLTextAreaElement | null) => {
      if (textarea) {
        textarea.style.height = "auto";
        textarea.style.height = `${textarea.scrollHeight}px`;
      }
    };

    const adjustHeight1 = () => {
      adjustHeight(searchInput1.value);
      searchQuery.value = searchInput1.value?.value || "";
    };

    const adjustHeight2 = () => {
      adjustHeight(searchInput2.value);
    };

    onMounted(() => {
      adjustHeight1();
      animateSentences();
    });

    const currentScreen = ref(1);

    const switchToScreen2 = async () => {
      currentScreen.value = 2;
      await nextTick();
      adjustHeight2();
    };

    const typedSentence = ref("");
    const sentences = ref([
      "The smartest way to legal research",
      "Just enter the legal issue or a brief answer to any legal issue",
      "Optionally, you can include brief facts of the case",
    ]);
    const currentSentenceIndex = ref(0);

    const typeSentence = (sentence: string, delay: number) => {
      let i = 0;
      return new Promise<void>((resolve) => {
        const intervalId = setInterval(() => {
          typedSentence.value += sentence.charAt(i);
          i++;
          if (i === sentence.length) {
            clearInterval(intervalId);
            setTimeout(() => {
              resolve();
            }, delay);
          }
        }, 40);
      });
    };

    const animateSentences = async () => {
      const sentence = sentences.value[currentSentenceIndex.value];
      await typeSentence(sentence, 2000);
      typedSentence.value = "";
      currentSentenceIndex.value =
        (currentSentenceIndex.value + 1) % sentences.value.length;
      setTimeout(animateSentences, 500); // Adjust the delay as needed
    };

    const showReaderView = ref(false);
    const selectedContent = ref("");

    const openReaderView = (content: string) => {
      selectedContent.value = content;
      showReaderView.value = true;
    };

    const closeReaderView = () => {
      showReaderView.value = false;
    };

    return {
      citations,
      selectedCitation,
      selectCitation,
      adjustHeight1,
      adjustHeight2,
      searchInput1,
      searchInput2,
      searchQuery,
      buttonHover,
      currentScreen,
      switchToScreen2,
      sentences,
      currentSentenceIndex,
      typedSentence,
      showReaderView,
      selectedContent,
      openReaderView,
      closeReaderView,
    };
  },
});
</script>

<style scoped>

.gradient-box {
  height: 98vh;
  background: linear-gradient(#F1F0E8 80%, #ffffff 100%);
}


.subtitle {
  background: linear-gradient(to right,
      #848484 20%,
      #848484 40%,
      #ffffff 65%,
      #848484 100%);
  color: black;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  padding: 10px;
}

.search-input {
  margin-top: 20px;
}


.sentence {
  opacity: 0;
  animation: typing 2s steps(30, end) forwards;
}

@keyframes typing {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

.search-input {
  max-height: 65px;
  /* Maximum height for the input */
  height: 40px;
  /* Default height for the input */
  overflow-y: auto;
  /* Enable vertical scrolling */
  white-space: pre-wrap;
  /* Wrap text inside the input */
  resize: none;
  /* Prevent manual resizing */
}
</style>
