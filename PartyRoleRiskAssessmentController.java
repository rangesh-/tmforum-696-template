// PartyRoleRiskAssessmentController.java
@RestController
@RequestMapping("/tmf-api/riskManagement/v4/partyRoleRiskAssessment")
public class PartyRoleRiskAssessmentController {

    @Autowired
    private PartyRoleRiskAssessmentService service;

    @GetMapping
    public ResponseEntity<List<PartyRoleRiskAssessment>> listPartyRoleRiskAssessments(
            @RequestParam(required = false) String status) {
        return ResponseEntity.ok(service.findAll(status));
    }

    @GetMapping("/{id}")
    public ResponseEntity<PartyRoleRiskAssessment> getPartyRoleRiskAssessment(
            @PathVariable String id) {
        return ResponseEntity.ok(service.findById(id));
    }

    @PostMapping
    public ResponseEntity<PartyRoleRiskAssessment> createPartyRoleRiskAssessment(
            @RequestBody PartyRoleRiskAssessmentCreate assessment) {
        PartyRoleRiskAssessment created = service.create(assessment);
        return ResponseEntity.created(URI.create("/" + created.getId())).body(created);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deletePartyRoleRiskAssessment(
            @PathVariable String id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
