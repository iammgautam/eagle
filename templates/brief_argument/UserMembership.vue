<template>
  <div class="gradient-box from-[#F1F0E8] to-[#ffffff] p-4 relative overflow-hidden h-screen">
    <div class="relative flex flex-col items-center text-center font-epilogue"
      :class="{ 'mt-10': !isTransitioning, 'mt-6': isTransitioning }">
      <p class="text-[#28261B] mb-4 text-4xl lg:text-4xl">LexPlore</p>
      <p v-if="!isTransitioning" class="text-[#28261B] w-full text-base lg:text-xl -mt-3">
        India's most advanced legal research search box
      </p>
    </div>

    <div
      :class="['search-container flex-grow flex items-center justify-center', { 'transition-active': isTransitioning }]">
      <div class="relative w-full max-w-[950px]" :class="{ 'max-w-[950px]': isTransitioning }">
        <div class="flex flex-col items-center justify-center">
          <div class="flex items-center justify-center w-full">
            <textarea ref="searchInput" v-model="searchQuery" placeholder="Search..." :class="[
              'search-input font-inter shadow-lg text-lg rounded-2xl pl-4 pr-4 py-2',
              {
                'w-[950px] border-2 border-gray-600': !isTransitioning,
                'w-[700px] border border-gray-400': isTransitioning
              }
            ]" @input="adjustHeight" rows="1" :style="{
              height: 'auto',
              minHeight: isTransitioning ? '42px' : '100px',
              maxHeight: isTransitioning ? '9vh' : '16vh',
              overflowY: 'auto',
            }"></textarea>
            <button :class="[
              'search-button font-inter shadow-lg mt-4 px-4 py-2 rounded-2xl cursor-pointer transition-all duration-300 ml-3',
              {
                'bg-[#BA5B37] bg-opacity-85 text-[#FFFFFF]': !searchQuery && !buttonHover,
                'bg-[#BA5B37] text-[#FFFFFF]': searchQuery || buttonHover,
                'bg-[#BA5B38] bg-opacity-85 text-[#FFFFFF]': buttonHover,
              }
            ]" @mouseover="buttonHover = true" @mouseleave="buttonHover = false" @click="startTransition">
              <span v-if="!isTransitioning" class="w-20 inline-block text-medium text-lg">Search</span>
              <svg v-else class="w-4 h-4 mx-auto" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 10l7-7m0 0l7 7m-7-7v18" />
              </svg>
            </button>
          </div>
          <div v-if="isTransitioning" class="w-full text-center text-sm text-gray-600 mt-1 pr-2">
            {{ citations.length }} results found
          </div>
          <div v-if="!isTransitioning" class="mt-4 text-center text-[#1F2837] font-epilogue h-6">
            <div class="text-sm">
              <span class="sentence">{{ typedSentence }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>


    <div :class="['results-container', { 'show-results': isTransitioning }]">
      <div class="results flex border rounded-lg shadow-lg bg-[#F8F8F8] border-[#a8a8a8] p-4 mt-8 h-[540px] flex-col">
        <div class="flex flex-1">
          <div class="w-2/5 p-4 flex flex-col border-r border-gray-300">
            <h2 class="text-lg font-medium mb-3 -mt-4 text-left font-epilogue">Authority</h2>
            <div class="overflow-y-auto leading-relaxed text-[#050142] font-inter"
              style="max-height: 460px; font-size: 14px;">
              <ul>
                <li v-for="(citation, index) in sortedCitations" :key="index" :class="[
                  'my-3 cursor-pointer hover:underline',
                  {
                    'font-bold text-[#050142]': index === selectedCitation,
                  },
                ]" @click="selectCitation(index)">
                  <div>{{ citation.petitioner_name }} v. {{ citation.respondent_name }}</div>
                  <div class="text-sm text-gray-600">in {{ citation.court }}</div>
                </li>
              </ul>
            </div>
          </div>
          <div class="w-3/5 p-4 flex flex-col">
            <h2 class="text-lg font-medium mb-4 -mt-4 text-left font-epilogue font-inter">Case Text</h2>
            <div class="overflow-y-auto" style="max-height: 460px">
              <div v-if="selectedCitation !== null">
                <div v-for="(paragraph, index) in sortedParagraphs" :key="index" :class="[
                  'bg-[#F3F4ED] text-[#28261B] shadow-sm border border-gray-200 hover:border hover:border-none rounded-lg p-4 mb-4 leading-relaxed relative text-justify',
                  { 'font-bold': index === 0 }
                ]" style="font-size: 14px; height: 180px;">
                  <div class="overflow-y-auto h-full pr-8" @click="openReaderView(paragraph.text)">
                    {{ paragraph.text }}
                  </div>
                  <div class="absolute bottom-2 right-2" @mouseenter="hoveredIndex = index"
                    @mouseleave="hoveredIndex = null">
                    <div :class="[
                      'p-2 rounded-lg transition-all duration-200 ease-in-out',
                      { 'bg-[#dad4c0]': hoveredIndex === index }
                    ]">
                      <ClipboardIcon v-if="!copiedStates[index]" class="w-5 h-5 cursor-pointer"
                        @click.stop="copyToClipboard(paragraph.text, index)" />
                      <CheckIcon v-else class="w-5 h-5 text-green-600" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <h2
      class="text-[#28261B] text-center font-semibold font-inter absolute bottom-0 left-1/2 transform -translate-x-1/2">
      SYNDICUS
    </h2>
  </div>

  <div v-if="showReaderView" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50"
    @click.self="closeReaderView">
    <div class="bg-white w-[180mm] h-[200mm] p-8 overflow-y-auto">
      <p class="text-gray-700 text-lg text-justify font-inter leading-relaxed">
        {{ selectedContent }}
      </p>
    </div>
  </div>
</template>


<script lang="ts">
import { defineComponent, ref, onMounted, nextTick, computed } from "vue";
import { ClipboardIcon, CheckIcon } from 'lucide-vue-next';



export default defineComponent({
  name: "UserMembership",
  components: {
    ClipboardIcon,
    CheckIcon,
  },
  setup() {
    const citations = ref([
      {
        id: 123,
        case: "AIR 2023 SUPREME COURT 49",
        respondent_name: "Mehdi Hasan (Deceased) Thr. LR.s.",
        petitioner_name: "Lucknow Development Authority",
        court: "Supreme Court of India",
        ratio_score: 0.8,
        paragraph_value: [
          {
            id: 1,
            text: "On behalf of the state, it was argued by Mr. Yashraj Singh Bundela, learned counsel, that no interference with the concurrent findings of the courts below is called for and that the appeal involves appreciation of evidence. As there is nothing that can be termed as perverse or unreasonable as regards these findings, which are based on the evidence led, this court should not exercise its discretionary jurisdiction to upset or interfere with the findings.",
            para_score: 0.6
          },
          {
            id: 2,
            text: "It is submitted that the appellant is a manufacturer of crown corks used for sealing glass bottles. Initially, it was producing 'Spun Line Crown Corks'. However, subsequently, it diversified the manufacturing activity to manufacture 'Double Lip Dry Blend Crowns' for which it imported new plant and machinery and invested a fixed capital cost of Rs. 4.5 crores.",
            para_score: 0.9
          },
          {
            id: 3,
            text: "test It is submitted that the appellant is a manufacturer of crown corks used for sealing glass bottles. Initially, it was producing 'Spun Line Crown Corks'. However, subsequently, it diversified the manufacturing activity to manufacture 'Double Lip Dry Blend Crowns' for which it imported new plant and machinery and invested a fixed capital cost of Rs. 4.5 crores.",
            para_score: 0.5
          }
        ]
      },
      {
        "id": 456,
        "case": "AIR 2023 SUPREME COURT 163",
        "respondent_name": "Rohtash Singh",
        "petitioner_name": "Desh Raj ",
        "court": "Supreme Court of India",
        "ratio_score": 0.4,
        "paragraph_value": [
          {
            "id": 1,
            "text": "Per contra, the Appellants have heavily relied on the following passage of the decision of this Court in Satish Batra11to justify the forfeiture of earnest money -          '15. The law is, therefore, clear that to justify the forfeiture of advance money being part of 'earnest money' the terms of the contract should be clear and explicit. Earnest money is paid or given at the time when the contract is entered into and, as a pledge for its due performance by the depositor to be forfeited in case of non-performance by the depositor. There can be converse situation also that if the seller fails to perform the contract the purchaser can also get double the amount, if it is so stipulated. It is also the law that part-payment of purchase price cannot be forfeited unless it is a guarantee for the due performance of the contract. In other words, if the payment is made only towards part-payment of consideration and not intended as earnest money then the forfeiture clause will not apply.' In sum and substance, the Apply.'          In sum and substance, the Appellants contend that forfeiture of sum is justified when it is - (a) clearly stipulated as earnest money; (b) forms part of sale consideration and (c) intended to be in the nature of 'guarantee for the due performance of the contract', and (d) the binding agreement between the parties provides its forfeiture in the event of breach of contract.",
            "para_score": 0.6
          },
          {
            "id": 2,
            "text": "Therefore, in light of the abovementioned discussions, it can be seen that the practice of filing preliminary reports before the enactment of the present CrPC has now taken the form of filing charge-sheets without actually completing the investigation, only to scuttle the right of default bail. If we were to hold that charge-sheets can be filed without completing the investigation, and the same can be used for prolonging remand, it would in effect negate the purpose of introducing section 167(2) of the CrPC and ensure that the fundamental rights guaranteed to accused persons is violated.           28.We have carefully perused the judgments relied upon by the learned counsel for the respondent, however, none of the judgments relied upon permit the abuse of remand under Section 309(2) of the CrPC by permitting the filing of incomplete charge-sheets only to scuttle the right of statutory bail.",
            "para_score": 0.9
          }
        ]
      },
      {
        "id": 789,
        "case": "AIR 2023 SUPREME COURT 44",
        "respondent_name": "Lokendra Rathod",
        "petitioner_name": "Smt. Anjali ",
        "court": "Supreme Court of India",
        "ratio_score": 0.5,
        "paragraph_value": [
          {
            "id": 1,
            "text": "The Appellants are the heirs and legal representatives of Rajesh (deceased) who died as a result of a motor accident on 15th August 2010. He was travelling in a Maruti Alto Car bearing Registration No. MP-09- HE-3322, on reaching Badwah Road, a bus bearing Registration No. MP- 09-FA-3169 being driven by Respondent No.2 in a rash and negligent manner crashed into the Rajesh's car, resulting in Rajesh (deceased) receiving grievous injuries on various body parts, he later succumbed to the injuries during treatment. He is survived by his two          wives, three children and his parents, who are the appellants before this Court.",
            "para_score": 0.6
          },
          {
            "id": 2,
            "text": "This is the second paragraph with some relevant details.",
            "para_score": 0.9
          }
        ]
      }
      // ... (add the other two citation objects here)
    ]);
    const selectedCitation = ref<number | null>(0);
    const searchQuery = ref("");
    const buttonHover = ref(false);
    const hoveredIndex = ref<number | null>(null);
    const copiedStates = ref<boolean[]>([]);
    const searchInput = ref<HTMLTextAreaElement | null>(null);
    const currentScreen = ref(1);




    const sortedCitations = computed(() => {
      return [...citations.value].sort((a, b) => b.ratio_score - a.ratio_score);
    });

    const sortedParagraphs = computed(() => {
      if (selectedCitation.value === null) return [];
      return [...sortedCitations.value[selectedCitation.value].paragraph_value]
        .sort((a, b) => b.para_score - a.para_score);
    });

    const selectCitation = (index: number) => {
      selectedCitation.value = index;
    };

    const copyToClipboard = (text: string, index: number) => {
      navigator.clipboard.writeText(text).then(() => {
        copiedStates.value[index] = true;
        setTimeout(() => {
          copiedStates.value[index] = false;
        }, 2000);
      });
    };


    const adjustHeight = () => {
      if (searchInput.value) {
        searchInput.value.style.height = 'auto';
        searchInput.value.style.height = `${searchInput.value.scrollHeight}px`;
      }
    };

    onMounted(() => {
      adjustHeight();
      animateSentences();
    });


    const switchToScreen2 = async () => {
      currentScreen.value = 2;
      await nextTick();
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
    const isTransitioning = ref(false);

    const startTransition = () => {
      isTransitioning.value = true;
    };



    return {
      citations,
      selectedCitation,
      sortedCitations,
      sortedParagraphs,
      selectCitation,
      copyToClipboard,
      hoveredIndex,
      copiedStates,
      adjustHeight,
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
      startTransition,
      isTransitioning
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


.search-container {
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.5s ease-in-out;
  position: absolute;
  left: 0;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
}

.search-container.transition-active {
  top: 90px;
  transform: translateY(0);
}

.search-input {
  transition: all 0.5s ease-in-out;
}

.search-button {
  transition: all 0.5s ease-in-out;
  height: auto;
  height: 60px;
  width: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.transition-active .search-button {
  height: 42px;
  width: 42px;
  padding: 0;
}

.results-container {
  opacity: 0;
  transform: translateY(100%);
  transition: all 0.5s ease-in-out;
  position: absolute;
  left: 0;
  right: 0;
  top: 180px;
  padding: 0 1rem;
}

.results-container.show-results {
  opacity: 1;
  transform: translateY(0);
}
</style>
