


const app = Vue.createApp({
    data(){
        return{
            patientName: "",
            patientDoB: "",
            appointmentDateTime: "",
            drugAllergies: "",
            appointmentID: ""
        }
    },
    created(){
        appointmentID=$_POST['apptID']
        
    },
    computed:{
        
    },
    methods:{
        
    }
}).mount("#main-container");