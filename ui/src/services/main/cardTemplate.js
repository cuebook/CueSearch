import apiService from "./api";

class CardTemplateServices {
    async getCardTemplates() {
        const response = await apiService.get("cueSearch/card-templates/");
        if (response.success) {
            return response.data
        }
        else {
            return []
        }
    }
    async addCardTemplates(payload) {
        const response = await apiService.post("cueSearch/card-templates/create/", payload);
        if (response.success) {
            return response
        }
        else {
            return
        }
    }



}


let cardTemplateServices = new CardTemplateServices();
export default cardTemplateServices;
