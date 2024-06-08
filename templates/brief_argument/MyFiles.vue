<template>
  <div class="relative min-h-screen">
    <!-- Sidebar for headings -->
    <div class="hidden lg:block fixed inset-y-0 left-0 w-64 z-10">
      <div class="sticky top-1/3 transform -translate-y-1/2 p-4 ml-6" style="font-family: 'Tinos', serif;">
        <ul class="space-y-4">
          <li>
            <a :class="{
              'text-black': activeSection === 'question',
              'text-gray-500 hover:text-black': activeSection !== 'question'
            }" class="cursor-pointer transition-colors duration-300 block pb-2 border-b border-gray-300 mb-2"
              @click="scrollToSection('question')">
              Question Presented
            </a>
          </li>
          <li>
            <a :class="{
              'text-black': activeSection === 'facts',
              'text-gray-500 hover:text-black': activeSection !== 'facts'
            }" class="cursor-pointer transition-colors duration-300 block pb-2 border-b border-gray-300 mb-2"
              @click="scrollToSection('facts')">
              Statement of Facts
            </a>
          </li>
          <li v-for="(subsection, index) in analysisSubsections" :key="index">
            <a :class="{
              'text-black': activeSection === 'analysis-' + index,
              'text-gray-500 hover:text-black': activeSection !== 'analysis-' + index
            }" class="cursor-pointer transition-colors duration-300 block pb-2 border-b border-gray-300 mb-2"
              @click="scrollToSection('analysis-' + index)">
              {{ subsection.title }}
            </a>
          </li>
          <li>
            <a :class="{
              'text-black': activeSection === 'conclusion',
              'text-gray-500 hover:text-black': activeSection !== 'conclusion'
            }" class="cursor-pointer transition-colors duration-300 block pb-2 border-b border-gray-300 mb-2"
              @click="scrollToSection('conclusion')">
              Conclusion
            </a>
          </li>
          <li class="mt-6">
            <button @click="downloadPdf"
              class="w-full bg-blue-500 text-white py-2 px-4 rounded mb-2 hover:bg-blue-600 transition-colors duration-300">
              Download PDF
            </button>
            <button @click="copyToClipboard"
              class="w-full bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600 transition-colors duration-300">
              Copy for Word
            </button>
          </li>
        </ul>
      </div>
    </div>

    <!-- Main content -->
    <div class="flex justify-center items-start min-h-screen pt-16 md:pt-8">
      <div class="w-full max-w-3xl px-4 md:px-8">
        <h1 class="text-3xl md:text-4xl font-bold mb-10 text-left"
          style="font-family: Tinos; font-style: normal; font-weight: 600;">{{ memotitle }}</h1>
        <div>
          <section id="question" class="mb-8">
            <h2 class="text-zinc-900 text-xl md:text-2xl font-bold mb-2"
              style="font-family: Tinos; font-style: normal; font-weight: 600;">Question Presented</h2>
            <p class="text-zinc-800 text-l md:text-xl text-justify"
              style="font-family: Tinos; font-style: normal; font-weight: 400; line-height: 1.7;">{{ questionContent }}
            </p>
          </section>
          <section id="facts" class="mb-8">
            <h2 class="text-zinc-900 text-xl md:text-2xl font-bold mb-2"
              style="font-family: Tinos; font-style: normal; font-weight: 600;">Statement of Facts</h2>
            <p class="text-zinc-800 text-l md:text-xl text-justify"
              style="font-family: Tinos; font-style: normal; font-weight: 400; line-height: 1.7;">{{ factsContent }}</p>
          </section>
          <h2 class="text-xl md:text-2xl font-bold mb-2"
            style="font-family: Tinos; font-style: normal; font-weight: 600;">Discussion</h2>
          <section v-for="(subsection, index) in analysisSubsections" :key="index" :id="'analysis-' + index"
            class="mb-8">
            <h2 class="text-gray-900 text-xl md:text-2xl font-bold mb-2"
              style="font-family: Tinos; font-style: normal; font-weight: 400;">{{ subsection.title }}</h2>
            <div v-html="subsection.content" class="text-zinc-800 text-l md:text-xl text-justify"
              style="font-family: Tinos; font-style: normal; font-weight: 400; line-height: 1.7;"></div>
          </section>
          <section id="conclusion" class="mb-8">
            <h2 class="text-zinc-900 text-xl md:text-2xl font-bold mb-2"
              style="font-family: Tinos; font-style: normal; font-weight: 600;">Conclusion</h2>
            <p class="text-zinc-800 text-l md:text-xl text-justify"
              style="font-family: Tinos; font-style: normal; font-weight: 400; line-height: 1.7;">{{ conclusionContent
              }}</p>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>



<script>
import { defineComponent, ref, onMounted } from 'vue';
// import { jsPDF } from 'jspdf';


export default defineComponent({
  name: 'MyFiles',
  setup() {
    const memotitle = ref('Whether the divorce petition filed by Neha before Hon’ble Supreme Court is justified or not?');
    const questionContent = ref('Whether the Supreme Court of India should grant a divorce to Neha on the grounds of irretrievable breakdown of marriage and adultery by her husband Rahul, and whether the Court was justified in dismissing her previous petitions before the Family Court and High Court.');
    const factsContent = ref("Neha and Sachin, both 2006 IPS batch officers, married in 2006 under the Special Marriage Act, 1954 with parental consent. Sachin insisted on having a son, but Neha gave birth to two daughters, Pinki in 2007 and Priya in 2011, during their 5-year marriage. Quarrels over the lack of a male child led to a mutual consent divorce in 2012. Post-divorce in 2015, Neha married Rahul, another IPS officer she met after her transfer to Jaipur. Neha focused on her career, decided against having more children within 5 years, and allegedly neglected Rahul. In December 2016, Neha relocated to Delhi with her daughters, telling them Rahul was not their father. Meanwhile, Rahul hired a 17-year-old domestic worker, Rani, in Jaipur. They developed a live-in relationship resulting in Rani's pregnancy, which Neha discovered in November 2017. Neha filed for divorce in Family Court on grounds of irretrievable breakdown and adultery. The Family Court and High Court dismissed her petitions due to lack of specific legal provisions. Neha then approached the Supreme Court. Separately, Rani filed for maintenance against Rahul under the Domestic Violence Act, 2005. The Family Court and High Court rejected her claim as their relationship was adulterous. Rani then petitioned the Supreme Court.");
    const conclusionContent = ref("Based on the legal analysis, it appears unlikely that the Supreme Court would grant divorce to Neha on the grounds pleaded by her. Irretrievable breakdown of marriage is currently not a statutory ground under the Hindu Marriage Act, 1955, unless accompanied by other recognized reasons. Neha's allegation of adultery against Rahul, if proven, could be a valid basis for divorce. However, the invocation of Article 142 to grant divorce appears doubtful, unless Neha demonstrates a compelling case of grave injustice. Similarly, the Supreme Court is unlikely to overrule the High Court's dismissal of Rani's maintenance petition. The existing legal position bars a woman in an adulterous live-in relationship from claiming economic rights under the Protection of Women from Domestic Violence Act, 2005. As a next step, Neha should consider whether she can substantiate her charge of adultery against Rahul, or prove any other grounds recognized by the Hindu Marriage Act, 1955, to bolster her case for divorce. The Court will scrutinize all available evidence before deciding the matter. Overall, while the outcome cannot be predicted with certainty, Neha's legal position does not appear to be very strong based on current laws.");
    const analysisSubsections = ref([
      { title: 'Grounds for Divorce under the Hindu Marriage Act, 1955', content: "The Hindu Marriage Act, 1955 governs divorces for Hindus, Buddhists, Jains and Sikhs. Under Section 13, the Act allows divorce on grounds including adultery, cruelty, desertion, conversion, unsoundness of mind, virulent and incurable leprosy, venereal disease, renunciation, and no resumption of cohabitation after a decree of judicial separation for at least one year. However, the Act does not recognize 'irretrievable breakdown of marriage' as a ground for divorce. In the present case, Neha has sought divorce on this ground along with adultery. While adultery is a valid reason, irretrievable breakdown is not an independent ground unless it is accompanied by other legally recognized factors like cruelty or desertion for the statutory period. The Supreme Court, in its landmark judgments like Naveen Kohli v. Neelu Kohli (2006) and Vishnu Dutt Sharma v. Manju Sharma (2009), has recommended the Union government to amend the Act to make irretrievable breakdown a ground for divorce. However, currently it is not a legal provision. Therefore, Neha's plea for divorce solely based on irretrievable breakdown, in absence of other grounds like cruelty, may not succeed as per existing divorce laws. Her allegation of adultery against Rahul could be a valid reason if proven adequately." },
      { title: 'Live-in Relationships and Maintenance Rights', content: "Live-in relationships are not illegal per se in India. The Protection of Women from Domestic Violence Act, 2005 provides certain protections and rights to women in such relationships. Section 2(f) of the 2005 Act defines a 'domestic relationship' as one where two persons live or have lived together in a shared household when they are related by marriage or a relationship in the nature of marriage. Supreme Court judgments like Indra Sarma v. VKV Sarma (2013) have held that a live-in relationship will be considered a 'relationship in the nature of marriage' under the Act if it meets certain conditions demonstrating permanence and continuity. However, the 2005 Act also clarifies that no woman in an adulterous relationship can claim maintenance from her partner. If a man and woman are both married to other people during their live-in relationship, the woman cannot claim economic rights. In this case, Rahul was in a live-in arrangement with Rani while still being legally married to Neha. As per the existing position of law, Rani would not be entitled to maintenance from Rahul under the 2005 Act since their relationship would be considered adulterous. The High Court was therefore justified in dismissing her petition." },
      // Add more subsections as needed
    ]);
    const activeSection = ref('');

    const scrollToSection = (sectionId: string) => {
      const element = document.getElementById(sectionId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
        activeSection.value = sectionId;
      }
    };

    const handleScroll = () => {
      const sections = ['question', 'facts', ...analysisSubsections.value.map((_, index) => 'analysis-' + index), 'conclusion'];
      for (const section of sections) {
        const element = document.getElementById(section);
        if (element) {
          const rect = element.getBoundingClientRect();
          if (rect.top >= 0 && rect.bottom <= (window.innerHeight || document.documentElement.clientHeight)) {
            activeSection.value = section;
            break;
          }
        }
      }
    };

    onMounted(() => {
      window.addEventListener('scroll', handleScroll);
    });


    const generateHTML = () => {
      const content = `
        <html>
        <head>
          <style>
            body { font-family: Times New Roman, serif; line-height: 1.5; }
            h1 { font-size: 16pt; font-weight: bold; }
            h2 { font-size: 14pt; font-weight: bold; }
            p { font-size: 12pt; text-align: justify; }
          </style>
        </head>
        <body>
          <h1>${memotitle.value}</h1>
          <h2>Question Presented</h2>
          <p>${questionContent.value}</p>
          <h2>Statement of Facts</h2>
          <p>${factsContent.value}</p>
          <h2>Discussion</h2>
          ${analysisSubsections.value.map(subsection => `
            <h2>${subsection.title}</h2>
            <p>${subsection.content.replace(/<\/?[^>]+(>|$)/g, "")}</p>
          `).join('')}
          <h2>Conclusion</h2>
          <p>${conclusionContent.value}</p>
        </body>
        </html>
      `;
      return content;
    };

    const downloadPdf = () => {
      const content = generateHTML();
      const doc = new jsPDF({
        orientation: 'p',
        unit: 'pt',
        format: 'a4',
        putOnlyUsedFonts: true,
        floatPrecision: 2,
      });

      doc.html(content, {
        callback: function (doc) {
          doc.save('legal_memo.pdf');
        },
        x: 50,
        y: 50,
        width: 495, // A4 width minus margins
        windowWidth: 1000 // Larger window width for better rendering
      });
    };

    const copyToClipboard = () => {
      const content = generateHTML();
      navigator.clipboard.writeText(content)
        .then(() => {
          alert('Content copied to clipboard! You can now paste it into a Word document.');
        })
        .catch(err => {
          console.error('Failed to copy: ', err);
          alert('Failed to copy. Please try again.');
        });
    };

    const downloadDocx = () => {
      const content = generateHTML();
      const blob = new Blob([content], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = 'legal_memo.docx';
      link.click();
      window.URL.revokeObjectURL(link.href);
    };

    return {
      memotitle,
      questionContent,
      factsContent,
      conclusionContent,
      analysisSubsections,
      activeSection,
      scrollToSection,
      downloadDocx,
      downloadPdf,
      copyToClipboard,
    };
  },
});
</script>