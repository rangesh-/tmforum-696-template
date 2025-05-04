// PartyRoleRiskAssessment.java
@Data
public class PartyRoleRiskAssessment {
    private String id;
    private String href;
    private String status;
    
    @JsonProperty("@baseType")
    private String baseType;
    
    @JsonProperty("@schemaLocation")
    private String schemaLocation;
    
    @JsonProperty("@type")
    private String type;
    
    private RelatedParty partyRole;
    private List<Characteristic> characteristics;
    private RelatedPlace place;
    private RiskAssessmentResult riskAssessmentResult;
}// RelatedParty.java
@Data
public class RelatedParty {
    private String id;
    private String href;
    private String name;
    private String role;
    
    @JsonProperty("@baseType")
    private String baseType;
    
    @JsonProperty("@referredType")
    private String referredType;
    
    @JsonProperty("@schemaLocation")
    private String schemaLocation;
    
    @JsonProperty("@type")
    private String type;
}

// RiskAssessmentResult.java
@Data
public class RiskAssessmentResult {
    private Float overallScore;
    private TimePeriod validFor;
    
    @JsonProperty("@baseType")
    private String baseType;
    
    @JsonProperty("@schemaLocation")
    private String schemaLocation;
    
    @JsonProperty("@type")
    private String type;
    
    private List<RiskScore> score;
}

// RiskScore.java
@Data
public class RiskScore {
    private String riskName; // Enum: IDConfidenceRisk, FraudRisk, BadPaymentRisk, CreditGamingRisk
    private Float score;
    
    @JsonProperty("@baseType")
    private String baseType;
    
    @JsonProperty("@schemaLocation")
    private String schemaLocation;
    
    @JsonProperty("@type")
    private String type;
}

