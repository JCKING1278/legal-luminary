/* candidates.c - Emit HTML table from hard-coded candidate data.
 * Recompile and run to regenerate HTML; changing candidates requires editing
 * candidates.h and recompiling.
 */
#include <stdio.h>
#include "candidates.h"

int main(void) {
    const char *cash1 = "$2,691,075.95";
    const char *cash2 = "$10,494.74";
    const char *cash3 = "$0.00";

    printf("<p class=\"intro-text\">Candidates for %s. Cash-on-hand as reported. To change this content, edit <code>candidates.h</code> and <code>candidates.c</code> in <code>candidates_c/</code> and recompile.</p>\n", CANDIDATES_DISTRICT);
    printf("<table class=\"candidates-table\" aria-label=\"Candidates and cash on hand\">\n");
    printf("<thead><tr><th>Candidate</th><th>Cash on hand</th></tr></thead>\n<tbody>\n");
    printf("<tr><td>%s</td><td>%s</td></tr>\n", CANDIDATE_1_NAME, cash1);
    printf("<tr><td>%s</td><td>%s</td></tr>\n", CANDIDATE_2_NAME, cash2);
    printf("<tr><td>%s</td><td>%s</td></tr>\n", CANDIDATE_3_NAME, cash3);
    printf("</tbody></table>\n");
    return 0;
}
