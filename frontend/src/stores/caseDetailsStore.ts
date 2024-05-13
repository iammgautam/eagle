import { defineStore } from 'pinia';

interface CaseDetailsState {
    petitionerName: string;
    respondentName: string;
    caseFacts: string;
    legalIssue: string;
}

export const useCaseDetailsStore = defineStore('caseDetails', {
    state: (): CaseDetailsState => ({
        petitionerName: '',
        respondentName: '',
        caseFacts: '',
        legalIssue: '',
    }),
    actions: {
        setPetitionerName(name: string) {
            this.petitionerName = name;
        },
        setRespondentName(name: string) {
            this.respondentName = name;
        },
        setCaseFacts(facts: string) {
            this.caseFacts = facts;
        },
        setLegalIssue(issue: string) {
            this.legalIssue = issue;
        },
    },
});