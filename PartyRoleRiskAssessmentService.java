// PartyRoleRiskAssessmentService.java
@Service
public class PartyRoleRiskAssessmentService {

    @Autowired
    private PartyRoleRiskAssessmentRepository repository;

    public List<PartyRoleRiskAssessment> findAll(String status) {
        if (status != null) {
            return repository.findByStatus(status);
        }
        return repository.findAll();
    }

    public PartyRoleRiskAssessment findById(String id) {
        return repository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("PartyRoleRiskAssessment not found"));
    }

    public PartyRoleRiskAssessment create(PartyRoleRiskAssessmentCreate createRequest) {
        // Validate mandatory fields
        if (createRequest.getPartyRole() == null || createRequest.getPartyRole().getId() == null) {
            throw new BadRequestException("partyRole with id is mandatory");
        }

        PartyRoleRiskAssessment assessment = new PartyRoleRiskAssessment();
        // Map fields from createRequest to assessment
        assessment.setStatus("InProgress");
        assessment.setPartyRole(createRequest.getPartyRole());
        assessment.setCharacteristics(createRequest.getCharacteristics());
        assessment.setPlace(createRequest.getPlace());
        
        // Perform risk assessment logic
        RiskAssessmentResult result = performRiskAssessment(assessment);
        assessment.setRiskAssessmentResult(result);
        assessment.setStatus("Completed");
        
        return repository.save(assessment);
    }

    private RiskAssessmentResult performRiskAssessment(PartyRoleRiskAssessment assessment) {
        // Actual risk assessment logic would go here
        RiskAssessmentResult result = new RiskAssessmentResult();
        result.setOverallScore(calculateOverallScore());
        result.setValidFor(new TimePeriod(Instant.now(), Instant.now().plus(30, ChronoUnit.DAYS)));
        
        List<RiskScore> scores = new ArrayList<>();
        scores.add(new RiskScore("IDConfidenceRisk", calculateIdConfidenceScore()));
        scores.add(new RiskScore("FraudRisk", calculateFraudRiskScore()));
        scores.add(new RiskScore("BadPaymentRisk", calculatePaymentRiskScore()));
        scores.add(new RiskScore("CreditGamingRisk", calculateCreditGamingScore()));
        
        result.setScore(scores);
        return result;
    }

    public void delete(String id) {
        repository.deleteById(id);
    }
}
